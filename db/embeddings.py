"""ATLAS — Track A embedding helper.

Single source of truth for turning text into the vectors stored in / searched against
memory_index.tag_embedding. Everything (record_decision, search_memory_index) embeds
through here so the model + dimension can never drift apart.

Provider: Gemini `gemini-embedding-001` (stand-in while AWS Bedrock is blocked).
Dimension: 1536 via Matryoshka truncation — MUST equal VECTOR(...) in db/schema.sql.

Two invariants this file enforces (TRACK_A §5.2):
  1. Stored tags and incoming queries use the SAME model at the SAME dimension. If either
     ever changes, ALL stored vectors must be regenerated together — never incrementally.
  2. Asymmetric retrieval task types: stored tags embed as RETRIEVAL_DOCUMENT, search
     queries as RETRIEVAL_QUERY. Gemini designs these two to be compared against each
     other — it improves search quality and is still the "same model, same dim" contract.

We L2-normalize every vector: Google notes truncated (<3072) embeddings aren't unit-length,
and normalizing makes cosine/dot-product behave consistently.
"""
import math
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")
EMBED_DIM = 1536  # MUST match VECTOR(...) in db/schema.sql

_client = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise SystemExit("GEMINI_API_KEY is missing from .env.")
        _client = genai.Client(api_key=key)
    return _client


def _l2_normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vec))
    return vec if norm == 0.0 else [x / norm for x in vec]


def _embed(text: str, task_type: str) -> list[float]:
    resp = _get_client().models.embed_content(
        model=EMBED_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=EMBED_DIM,
        ),
    )
    vec = resp.embeddings[0].values
    if len(vec) != EMBED_DIM:
        raise RuntimeError(f"embedding dim {len(vec)} != expected {EMBED_DIM}")
    return _l2_normalize(vec)


def embed_tag(tag: str) -> list[float]:
    """Embed a tag being STORED into memory_index."""
    return _embed(tag, "RETRIEVAL_DOCUMENT")


def embed_query(query_text: str) -> list[float]:
    """Embed an incoming SEARCH query."""
    return _embed(query_text, "RETRIEVAL_QUERY")


def to_pgvector(vec: list[float]) -> str:
    """Render a vector as the pgvector text literal for parameterized inserts/queries."""
    return "[" + ",".join(repr(x) for x in vec) + "]"


if __name__ == "__main__":
    # Self-test: a stored tag vs. a paraphrased query should score high; an unrelated
    # query should score low — proving embeddings capture meaning, not keywords.
    def cosine(a, b):
        return sum(x * y for x, y in zip(a, b))  # both are unit vectors

    tag = embed_tag("deprioritized mobile offline sync for SSO bandwidth")
    q_related = embed_query("why did we put the offline feature on hold?")
    q_unrelated = embed_query("what is our marketing budget for Q3?")

    print(f"Model={EMBED_MODEL}  dim={len(tag)}  (expected {EMBED_DIM})")
    print(f"  norm(tag) = {math.sqrt(sum(x*x for x in tag)):.4f}  (expected ~1.0)")
    print(f"  cosine(tag, related query)   = {cosine(tag, q_related):.3f}   <- want HIGH")
    print(f"  cosine(tag, unrelated query) = {cosine(tag, q_unrelated):.3f}   <- want LOW")
