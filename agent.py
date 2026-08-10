"""The Atlas agent — the tool-use loop over the REAL memory tools. [Track B]

The search -> fetch -> answer loop, now backed by Track A's CockroachDB tools, plus a
record_decision tool so the agent can APPEND new memory — a new revision of an existing
topic, or an entirely new topic. That write-back is the "act" step.

Requires in .env:  GEMINI_API_KEY, COCKROACH_DATABASE_URL   (+ pip install psycopg2-binary)
"""
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Track A's real tools live in db/ and import their siblings as top-level modules
# (`from connection import ...`), so we put db/ on sys.path and import `tools` directly.
_DB_DIR = os.path.join(os.path.dirname(__file__), "db")
if _DB_DIR not in sys.path:
    sys.path.insert(0, _DB_DIR)
import tools as memory  # db/tools.py: search_memory_index / fetch_decisions / record_decision

load_dotenv()

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-flash-latest")

_SYSTEM = """You are Atlas, an AI that answers questions about a company's decision history
and records new decisions as they happen.

Tools:
- search_memory_index(query_text): finds relevant decision topics (ids + tags + scores).
- fetch_decisions(id_list): returns the FULL records for specific decision ids.
- record_decision(topic, new_state, old_state, cause, trigger_event, tension): appends a
  NEW decision to memory.

Answering:
- NEVER answer a decision-history question from your own assumptions. Search first, then
  fetch the records you need, then answer from those.
- Call search_memory_index at most ONCE per question. If it returns an EMPTY list, there is
  no relevant record: say so plainly and STOP. Do not re-search with reworded queries.
- For "why did X change?" questions, contrast old_state vs new_state and cite cause and tension.
- Keep answers concise and grounded only in fetched records; never invent decisions.

Recording (append to memory):
- When the conversation establishes a NEW decision, a CHANGE to the company's stance on a
  topic, or a firm recommendation you have concluded, call record_decision to append it.
- Change to an EXISTING topic: first search/fetch the current belief, then reuse the EXACT
  same topic string, set old_state to that current belief and new_state to the new one.
- ENTIRELY NEW topic: use a fresh, short topic label and leave old_state empty.
- Fill cause / trigger_event / tension when the conversation makes them clear; otherwise omit.
- Do NOT record for pure lookup or "why" questions where nothing new was decided.
- After recording, briefly confirm to the user what was saved."""


def _record_decision(topic, new_state, old_state=None, cause=None,
                     trigger_event=None, tension=None, recorded_by="Strategy Agent"):
    """Wrapper so the model may omit optional fields; fills sensible defaults."""
    return memory.record_decision(
        topic=topic, old_state=old_state, new_state=new_state, cause=cause,
        trigger_event=trigger_event, tension=tension, recorded_by=recorded_by,
    )


# name -> the actual python function to run when the model asks for it
_TOOLS = {
    "search_memory_index": memory.search_memory_index,
    "fetch_decisions": memory.fetch_decisions,
    "record_decision": _record_decision,
}

# Plain-language descriptions the model reads (it never sees the python above)
_DECLARATIONS = [
    types.FunctionDeclaration(
        name="search_memory_index",
        description="Search the decision index for topics relevant to a question. "
                    "Returns candidate decision ids with short tags and similarity scores.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "query_text": {"type": "string", "description": "The user's question or search phrase."},
            },
            "required": ["query_text"],
        },
    ),
    types.FunctionDeclaration(
        name="fetch_decisions",
        description="Fetch the full decision records for a list of decision ids "
                    "(from a prior search). Returns old_state, new_state, cause, tension, etc.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "id_list": {
                    "type": "array", "items": {"type": "string"},
                    "description": "Decision ids to fetch (the decision_id values from a search).",
                },
            },
            "required": ["id_list"],
        },
    ),
    types.FunctionDeclaration(
        name="record_decision",
        description="Append a NEW decision to memory — a new revision of an existing topic, "
                    "or an entirely new topic. Use only when a real decision or change was made.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Topic label. Reuse the EXACT existing topic string for a change; a fresh short label for a new topic."},
                "new_state": {"type": "string", "description": "The new belief or decision."},
                "old_state": {"type": "string", "description": "The prior belief this replaces. Omit for a brand-new topic."},
                "cause": {"type": "string", "description": "What drove the change, if known."},
                "trigger_event": {"type": "string", "description": "What happened that prompted it, if known."},
                "tension": {"type": "string", "description": "What it traded off against, if known."},
            },
            "required": ["topic", "new_state"],
        },
    ),
]

_CONFIG = types.GenerateContentConfig(
    system_instruction=_SYSTEM,
    tools=[types.Tool(function_declarations=_DECLARATIONS)],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)


def answer(question: str, history: list[dict] | None = None) -> str:
    """Run the tool-use loop for one question and return Atlas's final text answer."""
    conversation = [types.Content(role="user", parts=[types.Part(text=question)])]

    for _ in range(8):  # safety cap against runaway loops
        response = _client.models.generate_content(model=_MODEL, contents=conversation, config=_CONFIG)

        if not response.function_calls:
            return response.text.strip()

        # The model can ask for several tools at once — run them all, answer them all.
        conversation.append(response.candidates[0].content)
        result_parts = []
        for call in response.function_calls:
            fn = _TOOLS[call.name]
            result = fn(**dict(call.args))
            result_parts.append(
                types.Part.from_function_response(name=call.name, response={"result": result})
            )
        conversation.append(types.Content(role="user", parts=result_parts))

    # Safety net: the model never settled. Force a final answer with tools OFF.
    conversation.append(types.Content(role="user", parts=[types.Part(
        text="Stop calling tools. Answer now using only what you have already found. "
             "If you found no relevant records, say Atlas has no record on this topic.")]))
    final = _client.models.generate_content(
        model=_MODEL, contents=conversation,
        config=types.GenerateContentConfig(system_instruction=_SYSTEM),
    )
    return final.text.strip()
