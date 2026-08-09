"""The Atlas agent — the tool-use loop, now over real memory tools. [Track B — Day 3]

This is `tool_use_demo.py` grown up: same loop, but with the two retrieval tools
registered instead of one fake one, plus a system instruction telling the model how
Atlas is supposed to behave.

Swap to real data on Day 4 by changing ONE line:
    import mock_memory as memory   ->   import memory.tools as memory
"""
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

import mock_memory as memory  # <-- the only line that changes on Day 4

load_dotenv()

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-flash-latest")

# The system instruction shapes HOW the agent uses its tools. This is where we tell
# it "don't answer from memory of your own — go look it up," which is the whole point.
_SYSTEM = """You are Atlas, an AI that answers questions about a company's decision history.

You have two tools:
- search_memory_index(query_text): finds relevant decision topics (returns ids + tags + scores).
- fetch_decisions(id_list): returns the FULL records for specific decision ids.

Rules:
- NEVER answer a decision-history question from your own assumptions. Search first,
  then fetch the records you need, then answer from those.
- Call search_memory_index at most ONCE per question. If it returns an EMPTY list, that
  means there is no relevant record: immediately tell the user Atlas has no record on this
  topic, and STOP. Do not search again with reworded queries.
- After a useful search, call fetch_decisions once for the ids you need, then answer.
- For "why did X change?" questions, contrast old_state vs new_state and cite the cause
  and tension fields explicitly.
- Keep answers concise and grounded only in the fetched records; never invent decisions."""

# name -> the actual python function to run when the model asks for it
_TOOLS = {
    "search_memory_index": memory.search_memory_index,
    "fetch_decisions": memory.fetch_decisions,
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
                    "description": "Decision ids to fetch, e.g. ['d2', 'd3'].",
                },
            },
            "required": ["id_list"],
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

    for _ in range(6):  # safety cap against runaway loops
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

    # Safety net: the model never settled. Force a final answer with tools OFF, so it
    # must reply in words instead of calling yet another tool.
    conversation.append(types.Content(role="user", parts=[types.Part(
        text="Stop searching. Answer now using only what you have already found. "
             "If you found no relevant records, say Atlas has no record on this topic.")]))
    final = _client.models.generate_content(
        model=_MODEL, contents=conversation,
        config=types.GenerateContentConfig(system_instruction=_SYSTEM),
    )
    return final.text.strip()
