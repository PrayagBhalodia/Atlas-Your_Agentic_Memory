"""The Atlas agents — every question is answered by three domain-constrained agents. [Track B]

For ANY question: the Finance agent and the Product agent each give their domain's read
(grounded in the shared CockroachDB memory), then the Strategy agent synthesizes both with
the decision history into the final answer — and, when the answer is a new decision or
recommendation, records it back to memory (the "act" write-back).

All three agents share one memory (Track A's tools). Chat runs on Gemini.
Requires in .env: GEMINI_API_KEY, COCKROACH_DATABASE_URL.
"""
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

_DB_DIR = os.path.join(os.path.dirname(__file__), "db")
if _DB_DIR not in sys.path:
    sys.path.insert(0, _DB_DIR)
import tools as memory  # db/tools.py: search_memory_index / fetch_decisions / record_decision

load_dotenv()

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-flash-latest")


# --- Tool declarations -------------------------------------------------------
_SEARCH_DECL = types.FunctionDeclaration(
    name="search_memory_index",
    description="Search the decision index for topics relevant to a question. "
                "Returns candidate decision ids with short tags and similarity scores.",
    parameters_json_schema={"type": "object", "properties": {
        "query_text": {"type": "string", "description": "The question or search phrase."}},
        "required": ["query_text"]},
)
_FETCH_DECL = types.FunctionDeclaration(
    name="fetch_decisions",
    description="Fetch the full decision records for a list of decision ids from a prior search.",
    parameters_json_schema={"type": "object", "properties": {
        "id_list": {"type": "array", "items": {"type": "string"},
                    "description": "Decision ids (the decision_id values from a search)."}},
        "required": ["id_list"]},
)
_RECORD_DECL = types.FunctionDeclaration(
    name="record_decision",
    description="Append a NEW decision to memory — a new revision of an existing topic, or an "
                "entirely new topic. Use only when a real decision or recommendation was made.",
    parameters_json_schema={"type": "object", "properties": {
        "topic": {"type": "string", "description": "Topic label; reuse the EXACT existing topic string for a change."},
        "new_state": {"type": "string", "description": "The new decision or recommendation."},
        "old_state": {"type": "string", "description": "Prior belief this replaces. Omit for a new topic."},
        "cause": {"type": "string", "description": "What drove it."},
        "trigger_event": {"type": "string", "description": "What prompted it."},
        "tension": {"type": "string", "description": "What it traded off against."}},
        "required": ["topic", "new_state"]},
)


# --- Persona system prompts (each agent is constrained to its own domain) -----
_MEMORY_RULES = (
    "Ground your view in recorded decisions: call search_memory_index first, then "
    "fetch_decisions for the ids you need. Never invent facts."
)
_FINANCE_SYSTEM = (
    "You are the Finance Agent for a startup. Consider ONLY the financial dimension — runway, "
    "burn rate, hiring and spend cost, cash safety. " + _MEMORY_RULES + " Give your view in "
    "2-4 sentences from finance's angle alone. If the question has no financial dimension, say "
    "briefly that Finance has little to add."
)
_PRODUCT_SYSTEM = (
    "You are the Product Agent for a startup. Consider ONLY the product dimension — roadmap, "
    "engineering workload, feature backlog, user impact. " + _MEMORY_RULES + " Give your view in "
    "2-4 sentences from product's angle alone. If the question has no product dimension, say "
    "briefly that Product has little to add."
)
_STRATEGY_SYSTEM = """You are the Strategy Agent for a startup. You are given a question plus the
Finance and Product agents' domain views, and you produce the final answer.

Tools: search_memory_index, fetch_decisions, record_decision.

- Ground the answer in the decision history: search and fetch the relevant records yourself.
- For questions about how or why something changed, walk the provenance — contrast old_state
  vs new_state and cite cause and tension.
- Weave in the Finance and Product views where relevant; if one had little to add, don't force it.
- If your answer is a NEW decision or recommendation (not a pure lookup), call record_decision
  to append it to memory.
- Be concise and grounded; never invent decisions."""


# --- Tools & the shared loop -------------------------------------------------
def _record_decision(topic, new_state, old_state=None, cause=None,
                     trigger_event=None, tension=None, recorded_by="Strategy Agent"):
    return memory.record_decision(topic=topic, old_state=old_state, new_state=new_state,
                                  cause=cause, trigger_event=trigger_event, tension=tension,
                                  recorded_by=recorded_by)


_SPECIALIST_TOOLS = {
    "search_memory_index": memory.search_memory_index,
    "fetch_decisions": memory.fetch_decisions,
}
_SPECIALIST_DECLS = [_SEARCH_DECL, _FETCH_DECL]

_STRATEGY_TOOLS = dict(_SPECIALIST_TOOLS, record_decision=_record_decision)
_STRATEGY_DECLS = [_SEARCH_DECL, _FETCH_DECL, _RECORD_DECL]


def _run(system: str, tool_map: dict, declarations: list, prompt: str) -> str:
    """Generic Gemini tool-use loop: run until the model answers in text."""
    config = types.GenerateContentConfig(
        system_instruction=system,
        tools=[types.Tool(function_declarations=declarations)],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    conversation = [types.Content(role="user", parts=[types.Part(text=prompt)])]
    for _ in range(8):  # safety cap
        response = _client.models.generate_content(model=_MODEL, contents=conversation, config=config)
        if not response.function_calls:
            return response.text.strip()
        conversation.append(response.candidates[0].content)
        result_parts = []
        for call in response.function_calls:
            result = tool_map[call.name](**dict(call.args))
            result_parts.append(types.Part.from_function_response(name=call.name, response={"result": result}))
        conversation.append(types.Content(role="user", parts=result_parts))
    conversation.append(types.Content(role="user", parts=[types.Part(
        text="Answer now using only what you have; if nothing relevant was found, say so.")]))
    final = _client.models.generate_content(
        model=_MODEL, contents=conversation,
        config=types.GenerateContentConfig(system_instruction=system))
    return final.text.strip()


def answer(question: str, history: list[dict] | None = None) -> str:
    """Run all three agents: Finance and Product each give their domain view, then Strategy
    synthesizes them with the decision history (and records new decisions)."""
    finance_view = _run(_FINANCE_SYSTEM, _SPECIALIST_TOOLS, _SPECIALIST_DECLS, question)
    product_view = _run(_PRODUCT_SYSTEM, _SPECIALIST_TOOLS, _SPECIALIST_DECLS, question)
    strategy_prompt = (
        f"Question: {question}\n\n"
        f"Finance Agent's view:\n{finance_view}\n\n"
        f"Product Agent's view:\n{product_view}\n\n"
        "Now produce the final answer."
    )
    return _run(_STRATEGY_SYSTEM, _STRATEGY_TOOLS, _STRATEGY_DECLS, strategy_prompt)
