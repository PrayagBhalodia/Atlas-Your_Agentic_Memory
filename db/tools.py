"""ATLAS — Track A tools: the §4 interface contract Track B's agent calls.

    search_memory_index(query_text, threshold, max_results) -> list[dict]
    fetch_decisions(id_list)                                 -> list[dict]
    record_decision(topic, old_state, new_state, cause,
                    trigger_event, tension, recorded_by)     -> dict

Text in, dicts out — Track B never sees a vector. The query embedding happens INSIDE
search_memory_index (same embeddings.py that stored the tags), which is what structurally
guarantees the "same model, same dimension" invariant on both sides (TRACK_A §5.2).
"""
from psycopg2.extras import RealDictCursor

from connection import get_conn
from embeddings import embed_tag, embed_query, to_pgvector


def search_memory_index(query_text: str,
                        threshold: float = 0.7,
                        max_results: int = 10) -> list[dict]:
    """Embed query_text, HNSW cosine search over memory_index.tag_embedding.
    Returns only rows scoring >= threshold (score = cosine similarity, 0..1).
    Each dict: {decision_id, topic, tag, sequence_num, score}.
    May return several rows with the SAME decision_id (multi-tag) — caller dedupes.
    """
    qvec = to_pgvector(embed_query(query_text))
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # <=> is cosine DISTANCE (vector_cosine_ops); similarity = 1 - distance.
            # ORDER BY <=> ... LIMIT is what lets the HNSW index do the work.
            cur.execute(
                """
                SELECT decision_id, topic, tag, sequence_num,
                       1 - (tag_embedding <=> %s::vector) AS score
                FROM memory_index
                ORDER BY tag_embedding <=> %s::vector
                LIMIT %s;
                """,
                (qvec, qvec, max_results),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    results = []
    for r in rows:
        score = float(r["score"])
        if score >= threshold:
            results.append({
                "decision_id": str(r["decision_id"]),
                "topic": r["topic"],
                "tag": r["tag"],
                "sequence_num": r["sequence_num"],
                "score": round(score, 4),
            })
    return results


def fetch_decisions(id_list: list[str]) -> list[dict]:
    """Fetch full decisions rows by id, in the order requested (missing ids dropped)."""
    if not id_list:
        return []
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, topic, old_state, new_state, cause, trigger_event,
                       tension, recorded_by, created_at
                FROM decisions
                WHERE id = ANY(%s::uuid[]);
                """,
                (list(id_list),),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    by_id = {str(r["id"]): r for r in rows}
    out = []
    for wanted in id_list:
        r = by_id.get(str(wanted))
        if r is None:
            continue
        out.append({
            "id": str(r["id"]),
            "topic": r["topic"],
            "old_state": r["old_state"],
            "new_state": r["new_state"],
            "cause": r["cause"],
            "trigger_event": r["trigger_event"],
            "tension": r["tension"],
            "recorded_by": r["recorded_by"],
            "created_at": r["created_at"].isoformat() if r["created_at"] else None,
        })
    return out


def list_decisions() -> list[dict]:
    """All decisions, grouped-ready (ordered by topic, then oldest-first within a topic).
    Used to render the full provenance timeline, including agent write-backs.
    """
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, topic, old_state, new_state, cause, trigger_event,
                       tension, recorded_by, created_at
                FROM decisions
                ORDER BY topic, created_at;
                """
            )
            rows = cur.fetchall()
    finally:
        conn.close()
    return [{
        "id": str(r["id"]),
        "topic": r["topic"],
        "old_state": r["old_state"],
        "new_state": r["new_state"],
        "cause": r["cause"],
        "trigger_event": r["trigger_event"],
        "tension": r["tension"],
        "recorded_by": r["recorded_by"],
        "created_at": r["created_at"].isoformat() if r["created_at"] else None,
    } for r in rows]


def _insert_decision(topic: str, old_state, new_state: str, cause, trigger_event,
                     tension, recorded_by: str, tag: str,
                     sequence_num: int | None = None) -> dict:
    """Dual-write: embed the tag, then INSERT the decisions row AND its memory_index
    row in ONE transaction (the app-level atomic write decided on Day 2). Shared by the
    seed loader (explicit tag/seq) and record_decision (derived tag, auto seq).
    """
    embedding = to_pgvector(embed_tag(tag))
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if sequence_num is None:
                cur.execute(
                    "SELECT COALESCE(MAX(sequence_num), 0) + 1 AS n "
                    "FROM memory_index WHERE topic = %s;",
                    (topic,),
                )
                sequence_num = cur.fetchone()["n"]

            cur.execute(
                """
                INSERT INTO decisions
                    (topic, old_state, new_state, cause, trigger_event, tension, recorded_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (topic, old_state, new_state, cause, trigger_event, tension, recorded_by),
            )
            decision_id = cur.fetchone()["id"]

            cur.execute(
                """
                INSERT INTO memory_index
                    (topic, decision_id, tag, tag_embedding, sequence_num)
                VALUES (%s, %s, %s, %s::vector, %s);
                """,
                (topic, decision_id, tag, embedding, sequence_num),
            )
        conn.commit()
        return {"id": str(decision_id)}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def record_decision(topic: str, old_state, new_state: str, cause, trigger_event,
                    tension, recorded_by: str) -> dict:
    """Insert a new decision + its index row (the agent's write-back). Returns {id}.

    The §4 signature carries no explicit tag, so we derive a short one for the index.
    Day 5 can upgrade this to an LLM-generated tag; a topic+new_state label embeds fine.
    """
    tag = f"{topic}: {new_state}"
    if len(tag) > 120:
        tag = tag[:117] + "..."
    return _insert_decision(topic, old_state, new_state, cause, trigger_event,
                            tension, recorded_by, tag)
