"""Mock memory tools. [Track B — Day 3]

Stands in for Track A's real CockroachDB functions. Same names, same inputs, same
output shapes as the contract in TRACK_A.md — so on Day 4 you swap `import mock_memory`
for `import memory.tools` and nothing else changes.

What's real here vs. mock:
- REAL: the search uses genuine Gemini embeddings + cosine similarity, so it matches on
  MEANING, not keywords — any phrasing of a question works, not a fixed vocabulary.
- MOCK: the data lives in a Python list instead of CockroachDB, and embeddings are held
  in memory instead of a vector index. That's the only difference from the finished thing.
"""
import math
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
_EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")

# Calibrated from real scores on 2026-08-10: relevant records scored 0.73-0.88,
# unrelated/noise scored <=0.56, so 0.65 sits in the gap with a buffer on both sides.
# NOTE: this number is specific to gemini-embedding-001 on THIS data — Track A will
# need to re-calibrate once real Titan/Gemini embeddings run over the real records.
DEFAULT_THRESHOLD = 0.65

# --- The fake "database": full decision rows (what fetch_decisions returns) ----
DECISIONS = [
    {
        "id": "d1", "topic": "mobile offline sync",
        "old_state": None,
        "new_state": "Build full offline sync for the mobile app this quarter.",
        "cause": "Early users on flaky connections asked for it repeatedly.",
        "trigger_event": "Q1 user interviews",
        "tension": "Competes with SSO work for the same two mobile engineers.",
        "recorded_by": "Product Agent", "created_at": "2026-01-12T00:00:00Z",
    },
    {
        "id": "d2", "topic": "mobile offline sync",
        "old_state": "Build full offline sync for the mobile app this quarter.",
        "new_state": "Deprioritize offline sync; ship a read-only cache instead.",
        "cause": "Two enterprise deals were blocked on SSO, worth more than the churn risk.",
        "trigger_event": "Enterprise deal review in February",
        "tension": "Traded power-user delight for near-term revenue.",
        "recorded_by": "Strategy Agent", "created_at": "2026-02-15T00:00:00Z",
    },
    {
        "id": "d3", "topic": "mobile offline sync",
        "old_state": "Deprioritize offline sync; ship a read-only cache instead.",
        "new_state": "Revisit full offline sync in H2, once SSO ships.",
        "cause": "SSO delivered; the two mobile engineers free up in July.",
        "trigger_event": "SSO GA milestone",
        "tension": "H2 roadmap is already crowded with the billing revamp.",
        "recorded_by": "Product Agent", "created_at": "2026-07-02T00:00:00Z",
    },
    {
        "id": "d4", "topic": "engineering headcount",
        "old_state": None,
        "new_state": "Hold at 6 engineers; hire only if runway stays above 12 months.",
        "cause": "Conservative cash posture after the bridge round.",
        "trigger_event": "Board guidance post-bridge",
        "tension": "Slower roadmap vs. cash safety.",
        "recorded_by": "Finance Agent", "created_at": "2026-03-01T00:00:00Z",
    },
    {
        "id": "d5", "topic": "engineering headcount",
        "old_state": "Hold at 6 engineers; hire only if runway stays above 12 months.",
        "new_state": "Approved one senior backend hire.",
        "cause": "New ARR pushed runway to 16 months; backlog risk outweighed the extra burn.",
        "trigger_event": "Q2 revenue review",
        "tension": "Higher burn, but shipping velocity was the bigger risk.",
        "recorded_by": "Strategy Agent", "created_at": "2026-06-20T00:00:00Z",
    },
]

# --- The "index": tiny pointer rows (what search scans) -----------------------
INDEX = [
    {"decision_id": "d1", "topic": "mobile offline sync", "tag": "committed to offline sync", "sequence_num": 1},
    {"decision_id": "d2", "topic": "mobile offline sync", "tag": "deprioritized for SSO bandwidth", "sequence_num": 2},
    {"decision_id": "d3", "topic": "mobile offline sync", "tag": "offline sync back on H2 roadmap", "sequence_num": 3},
    {"decision_id": "d4", "topic": "engineering headcount", "tag": "headcount held at six", "sequence_num": 1},
    {"decision_id": "d5", "topic": "engineering headcount", "tag": "approved one backend hire", "sequence_num": 2},
]


# --- Embedding helpers (this is the "real" part) ------------------------------
def _embed(texts: list[str]) -> list[list[float]]:
    """Turn a list of strings into a list of embedding vectors via Gemini."""
    resp = _client.models.embed_content(model=_EMBED_MODEL, contents=texts)
    return [e.values for e in resp.embeddings]


def _cosine(a: list[float], b: list[float]) -> float:
    """Similarity of two vectors: 1.0 = same meaning, ~0 = unrelated."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


# Index embeddings are computed lazily on the first search (so simply reading DECISIONS
# — e.g. for the Timeline page — doesn't spend an embedding call). Cached after first use.
_index_vectors = None


def _get_index_vectors() -> list[list[float]]:
    global _index_vectors
    if _index_vectors is None:
        _index_vectors = _embed([f"{e['topic']} — {e['tag']}" for e in INDEX])
    return _index_vectors


# --- The two retrieval tools (contract signatures) ----------------------------
def search_memory_index(query_text: str, threshold: float = DEFAULT_THRESHOLD, max_results: int = 10) -> list[dict]:
    """Semantic search: embed the query, compare to every index entry by cosine
    similarity, return the ones scoring >= threshold (not a fixed top-k)."""
    query_vec = _embed([query_text])[0]
    matches = []
    for entry, vec in zip(INDEX, _get_index_vectors()):
        score = _cosine(query_vec, vec)
        if score >= threshold:
            matches.append({
                "decision_id": entry["decision_id"], "topic": entry["topic"],
                "tag": entry["tag"], "sequence_num": entry["sequence_num"],
                "score": round(score, 3),
            })
    matches.sort(key=lambda m: m["score"], reverse=True)
    return matches[:max_results]


def fetch_decisions(id_list: list[str]) -> list[dict]:
    by_id = {d["id"]: d for d in DECISIONS}
    return [by_id[i] for i in id_list if i in by_id]
