"""ATLAS — Track A standalone retrieval test (no agent needed).

Runs a few natural-language questions through the REAL search_memory_index + fetch_decisions,
so you can eyeball scores and confirm the two-hop retrieval works before Track B wires it
into the agent on Day 4. Also the place to sanity-check the similarity threshold.

Run:  ./.venv/bin/python db/test_retrieval.py
"""
from tools import search_memory_index, fetch_decisions

THRESHOLD = 0.6  # deliberately below the 0.7 default — Gemini scores run compressed
MAX_RESULTS = 5

QUERIES = [
    "why did we stop working on mobile offline mode?",   # -> offline sync chain
    "how has our engineering hiring stance evolved?",     # -> headcount chain
    "how has our pricing changed over time?",             # -> pricing chain
    "what's the weather like today?",                     # unrelated -> expect no hits
]


def main() -> None:
    for q in QUERIES:
        print("=" * 78)
        print(f"Q: {q}")
        hits = search_memory_index(q, threshold=THRESHOLD, max_results=MAX_RESULTS)
        if not hits:
            print("  (no hits above threshold — correct if this question is unrelated)")
            continue

        print("  index hits:")
        for h in hits:
            print(f"    {h['score']:.3f}  [{h['topic']} #{h['sequence_num']}]  {h['tag']}")

        # dedupe decision_ids, preserving best-first order (the agent's job in real life)
        ids = list(dict.fromkeys(h["decision_id"] for h in hits))
        print("  fetched decisions (old -> new):")
        for d in fetch_decisions(ids):
            print(f"    • {d['old_state']}  ->  {d['new_state']}")
            print(f"        cause: {d['cause']}  |  by: {d['recorded_by']}")


if __name__ == "__main__":
    main()
