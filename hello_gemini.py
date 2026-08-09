"""ATLAS — Gemini connectivity check (TEMPORARY stand-in for Bedrock). [Track B]

Bedrock is still the real destination for submission (see hello.py) — this file only
exists because the AWS account is stuck in verification. Same two checks, same shape,
different provider, so nothing about *how* we think about the agent changes:
  1. Gemini answers a chat prompt        (the agent's brain, temporarily)
  2. Gemini returns an embedding vector  (the memory index's search key, temporarily)

Run:   python hello_gemini.py
Needs: pip install google-genai python-dotenv   (your job to install)
       GEMINI_API_KEY=... in .env

Once AWS clears, hello.py is the one that matters again — this file can be deleted.
"""
import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-flash-latest")
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")

if not API_KEY:
    raise SystemExit("GEMINI_API_KEY is missing from .env — add it and re-run.")

client = genai.Client(api_key=API_KEY)


def list_models() -> None:
    print("\n=== Models your Gemini API key can use ===")
    try:
        for m in client.models.list():
            actions = list(getattr(m, "supported_actions", None) or [])
            if "generateContent" in actions or "embedContent" in actions:
                print(f"  {m.name}   ({', '.join(actions)})")
    except genai_errors.APIError as e:
        print("  (couldn't list models):", e)


def test_chat() -> None:
    print(f"\n=== Test 1: Gemini chat  ({CHAT_MODEL}) ===")
    try:
        resp = client.models.generate_content(
            model=CHAT_MODEL,
            contents="Say hello in one short sentence.",
        )
        print("  Gemini says:", resp.text.strip())
        print("  PASS")
    except genai_errors.APIError as e:
        print("  FAIL:", e)
        print("  HINT: copy an exact model name from the list above into GEMINI_CHAT_MODEL in .env")


def test_embedding() -> None:
    print(f"\n=== Test 2: Gemini embedding  ({EMBED_MODEL}) ===")
    try:
        resp = client.models.embed_content(
            model=EMBED_MODEL,
            contents="mobile offline sync",
        )
        vec = resp.embeddings[0].values
        print(f"  Got a vector of length {len(vec)}.")
        print("  PASS")
        print("  NOTE: remember this length — it decides the VECTOR(...) size Track A")
        print("        uses in CockroachDB. Tell your teammate.")
    except genai_errors.APIError as e:
        print("  FAIL:", e)
        print("  HINT: copy an exact model name from the list above into GEMINI_EMBED_MODEL in .env")


if __name__ == "__main__":
    list_models()
    test_chat()
    test_embedding()
    print("\nDone. Two PASS lines = Gemini is ready to stand in for Bedrock while AWS verifies.")
