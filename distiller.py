"""Distiller agent. [Track B]

First stage of ingestion: take the raw text of a meeting/conversation that may cover
several topics and several strategy changes, and compress it into ONE clean record per
distinct change.

    file  ->  extract_text  ->  distiller.distill()  ->  record_decision()

This is STRUCTURED extraction, not lossy prose summarization: cause / trigger_event /
tension are kept as explicit fields, so the causal "why" survives. (The design forbids
summarizing the STORED provenance — here we only compress the messy raw INPUT into
structured records; the reasoning is preserved, never dropped.)
"""
import json
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

load_dotenv()

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-flash-lite-latest")
_MAX_CHARS = 120_000  # generous — a long meeting fits; absurdly large inputs get truncated

_SYSTEM = """You are Atlas's distiller. You receive the raw text of a meeting or conversation
that may cover several different topics and several strategy/decision changes, mixed with
discussion, tangents, and noise. Compress it into ONE clean record per distinct decision or
change of stance — lose nothing that matters, keep nothing that doesn't.

For each distinct change, output an object with:
- topic: a short, stable subject label. If it matches one of the KNOWN TOPICS listed below,
  reuse that EXACT string so the change extends the existing history; otherwise use a concise
  new label.
- old_state: the prior stance the conversation is changing FROM, if stated or clearly implied
  (else null).
- new_state: the decision or new stance, stated concisely.
- cause: the real reason it changed, in the participants' own logic (else null).
- trigger_event: what prompted it (else null).
- tension: what it traded off against (else null).
- date: the calendar date the decision was MADE, as YYYY-MM-DD, if the conversation makes it
  clear (e.g. the meeting date at the top, or an explicit date) — else null.

Rules:
- One object per real change. Merge repetitive back-and-forth about the same change into one.
- Do NOT invent facts; only compress what is actually there.
- Preserve the WHY: cause and tension must reflect the actual reasoning, never be dropped.
- Ignore chit-chat, logistics, and anything that isn't a decision or change of stance.
- If there are no real changes, return an empty list.
Return STRICT JSON: a list of these objects and nothing else.

KNOWN TOPICS (reuse these exact labels when applicable): {known}"""


def distill(text: str, known_topics: list[str] | None = None) -> list[dict]:
    """Compress raw conversation text into a list of structured change records."""
    if not text.strip():
        return []
    known = ", ".join(sorted(known_topics)) if known_topics else "(none yet)"
    prompt = _SYSTEM.format(known=known) + "\n\n--- CONVERSATION ---\n" + text[:_MAX_CHARS]
    # Short backoff-retry on transient 429/5xx; per-day quota exhaustion isn't retried.
    for attempt in range(3):
        try:
            resp = _client.models.generate_content(
                model=_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            break
        except genai_errors.APIError as e:
            if getattr(e, "code", None) not in (429, 500, 503) or "PerDay" in str(e) or attempt == 2:
                raise
            time.sleep(1.5 * (attempt + 1))
    try:
        data = json.loads(resp.text)
    except (json.JSONDecodeError, TypeError):
        return []
    return data if isinstance(data, list) else []
