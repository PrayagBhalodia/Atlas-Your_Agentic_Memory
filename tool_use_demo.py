"""ATLAS — Day 2: watching the tool-use loop, with one FAKE tool. [Track B]

Nothing here touches Atlas's real memory yet — that's Day 3. The only goal is to
*see* the loop mechanics with your own eyes, using one hardcoded tool, before we
point a real tool at real data.

THE LOOP:
    ask model -> model asks to call a tool -> we run it -> we hand back the result
    -> model asks for another tool, OR gives its final answer -> repeat until done

Run:  python day2_tool_use_demo.py
"""
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-flash-latest")


# --- Step 1: the fake tool -----------------------------------------------------
# A real Python function. The model can NEVER run this itself — it can only ASK
# us to run it, by name, with some arguments. We're the ones who actually call it.
SECRET_NUMBERS = {"atlas": 42, "cockroach": 7, "bedrock": 19}


def get_secret_number(name: str) -> int:
    """Look up a hardcoded 'secret number' for a name. Fake, on purpose."""
    return SECRET_NUMBERS.get(name.lower(), -1)


# --- Step 2: describe the tool to the model, in the model's language -----------
# This is NOT the Python function — it's a plain-language + schema description so
# the model knows the tool exists, what it's for, and what arguments it expects.
# The model only ever reads THIS description. It never sees your Python code.
tool_declaration = types.FunctionDeclaration(
    name="get_secret_number",
    description="Look up the secret number associated with a given name.",
    parameters_json_schema={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "The name to look up, e.g. 'atlas'"},
        },
        "required": ["name"],
    },
)

config = types.GenerateContentConfig(
    tools=[types.Tool(function_declarations=[tool_declaration])],
    # The SDK CAN run the whole loop for you invisibly ("automatic function
    # calling"). We turn that off on purpose today, so every step below happens
    # in OUR code and we can watch it happen.
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)

# Our own name -> function lookup, so we know what to run when the model asks.
AVAILABLE_TOOLS = {"get_secret_number": get_secret_number}


# --- Step 3: the loop itself -----------------------------------------------
def run_loop(question: str) -> None:
    print(f"\nYOU: {question}")

    # `conversation` is the full back-and-forth so far. It grows every step.
    conversation = [types.Content(role="user", parts=[types.Part(text=question)])]

    for step in range(5):  # safety cap — a buggy agent could loop forever otherwise
        response = client.models.generate_content(model=MODEL, contents=conversation, config=config)

        if not response.function_calls:
            # No tool requested — the model is ready to give its real answer.
            print(f"ATLAS: {response.text.strip()}")
            return

        # The model asked to call a tool. Look at exactly what it asked for.
        call = response.function_calls[0]
        print(f"  [step {step + 1}] model wants to call: {call.name}({dict(call.args)})")

        fn = AVAILABLE_TOOLS[call.name]
        result = fn(**call.args)
        print(f"  [step {step + 1}] we ran it ourselves -> result = {result}")

        # Feed BOTH turns back in: what the model asked for, and what we found.
        # Without this, the model has no memory of having asked the question.
        conversation.append(response.candidates[0].content)
        conversation.append(
            types.Content(
                # Gemini has no "tool" role (unlike Bedrock/Claude) — function
                # results are sent back under the "user" role instead.
                role="user",
                parts=[types.Part.from_function_response(name=call.name, response={"result": result})],
            )
        )

    print("ATLAS: (gave up after 5 steps — something's looping)")


if __name__ == "__main__":
    run_loop("What's the secret number for atlas?")
    run_loop("What's today's weather?")  