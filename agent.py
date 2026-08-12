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
import time
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors
from google.genai import types


_DB_DIR = os.path.join(os.path.dirname(__file__), "db")
if _DB_DIR not in sys.path:
    sys.path.insert(0, _DB_DIR)
import tools as memory  # db/tools.py: search_memory_index / fetch_decisions / record_decision

load_dotenv()

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
# Default to flash-lite: ~1000 free requests/day vs ~20 on the flagship — if the env var
# ever goes missing, the app degrades to a slower-quota model instead of dying mid-demo.
_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-flash-lite-latest")


def _generate(**kwargs):
    """generate_content with a short backoff-retry on transient 429/5xx, so one flaky
    call doesn't kill a whole multi-agent answer. Per-day quota exhaustion is not
    retried — waiting seconds can't fix a daily limit."""
    for attempt in range(3):
        try:
            return _client.models.generate_content(**kwargs)
        except genai_errors.APIError as e:
            if getattr(e, "code", None) not in (429, 500, 503) or "PerDay" in str(e) or attempt == 2:
                raise
            time.sleep(1.5 * (attempt + 1))


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


_MAX_HISTORY_TURNS = 6  # prior chat turns to carry so follow-ups have context


def _history_contents(history, current_question):
    """Turn prior chat messages into Gemini turns so follow-up questions ("why?",
    "what about Q3?") resolve against the conversation instead of starting cold.

    The UI passes st.session_state.messages, which (a) opens with a canned welcome and
    (b) already includes the just-asked question as its last item — we drop both so the
    history ends before the current turn and starts on a user turn.
    """
    if not history:
        return []
    turns = []
    for msg in history:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role")
        text = (msg.get("content") or "").strip()
        if role in ("user", "assistant") and text:
            turns.append((role, text))
    if turns and turns[-1][0] == "user" and turns[-1][1] == (current_question or "").strip():
        turns = turns[:-1]
    while turns and turns[0][0] == "assistant":  # drop leading welcome(s)
        turns = turns[1:]
    turns = turns[-_MAX_HISTORY_TURNS:]
    return [
        types.Content(role=("model" if role == "assistant" else "user"),
                      parts=[types.Part(text=text)])
        for role, text in turns
    ]


def _run(system, tool_map, declarations, prompt, on_event=None, agent="", history=None) -> str:
    """Generic Gemini tool-use loop: run until the model answers in text.
    `history` (Gemini Contents) seeds prior turns before this prompt for multi-turn context.
    on_event(dict), if given, receives tool_call / tool_result events for the thinking trace."""
    config = types.GenerateContentConfig(
        system_instruction=system,
        tools=[types.Tool(function_declarations=declarations)],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    conversation = list(history or [])
    conversation.append(types.Content(role="user", parts=[types.Part(text=prompt)]))
    for _ in range(8):  # safety cap
        response = _generate(model=_MODEL, contents=conversation, config=config)
        if not response.function_calls:
            return response.text.strip()
        conversation.append(response.candidates[0].content)
        result_parts = []
        for call in response.function_calls:
            args = dict(call.args)
            if on_event:
                on_event({"type": "tool_call", "agent": agent, "tool": call.name, "input": args})
            # A hallucinated tool name or malformed args must not crash the whole answer —
            # feed the error back as the tool result so the model can correct itself.
            # (SystemExit — e.g. missing DB URL — still propagates to the app's handler.)
            fn = tool_map.get(call.name)
            if fn is None:
                result = {"error": f"unknown tool '{call.name}' — use only the declared tools"}
            else:
                try:
                    result = fn(**args)
                except TypeError as e:
                    result = {"error": f"bad arguments for {call.name}: {e}"}
                except Exception as e:
                    result = {"error": f"{call.name} failed: {type(e).__name__}: {e}"}
            if on_event:
                on_event({"type": "tool_result", "agent": agent, "tool": call.name, "result": result})
            result_parts.append(types.Part.from_function_response(name=call.name, response={"result": result}))
        conversation.append(types.Content(role="user", parts=result_parts))
    conversation.append(types.Content(role="user", parts=[types.Part(
        text="Answer now using only what you have; if nothing relevant was found, say so.")]))
    final = _generate(
        model=_MODEL, contents=conversation,
        config=types.GenerateContentConfig(system_instruction=system))
    return final.text.strip()


def answer(question: str, history=None, on_event=None) -> str:
    """Run all three agents: Finance and Product each give their domain view, then Strategy
    synthesizes them with the decision history (and records new decisions).

    on_event(dict), if given, receives a live trace: agent_start / tool_call / tool_result /
    agent_view events — for the UI's "thinking" display.
    """
    def emit(ev):
        if on_event:
            on_event(ev)

    # Shared prior-turn context so every agent can resolve follow-up questions.
    hist = _history_contents(history, question)

    # Finance and Product are independent, so they run in parallel (the DB layer uses a
    # ThreadedConnectionPool for exactly this). Each thread buffers its trace events
    # locally; we emit them grouped from THIS thread afterwards — both for a readable
    # trace and because Streamlit UI callbacks may only run on the main script thread.
    def _specialist(name: str, system: str):
        events: list[dict] = []
        events.append({"type": "agent_start", "agent": name})
        view = _run(system, _SPECIALIST_TOOLS, _SPECIALIST_DECLS, question,
                    events.append, name, history=hist)
        events.append({"type": "agent_view", "agent": name, "text": view})
        return view, events

    emit({"type": "phase", "text": "Finance and Product are analyzing in parallel…"})
    with ThreadPoolExecutor(max_workers=2) as pool:
        finance_future = pool.submit(_specialist, "Finance", _FINANCE_SYSTEM)
        product_future = pool.submit(_specialist, "Product", _PRODUCT_SYSTEM)
        finance_view, finance_events = finance_future.result()
        product_view, product_events = product_future.result()
    for ev in finance_events + product_events:
        emit(ev)

    emit({"type": "agent_start", "agent": "Strategy"})
    strategy_prompt = (
        f"Question: {question}\n\n"
        f"Finance Agent's view:\n{finance_view}\n\n"
        f"Product Agent's view:\n{product_view}\n\n"
        "Now produce the final answer."
    )
    final = _run(_STRATEGY_SYSTEM, _STRATEGY_TOOLS, _STRATEGY_DECLS, strategy_prompt, on_event, "Strategy", history=hist)
    emit({"type": "agent_view", "agent": "Strategy", "text": final})
    return final
