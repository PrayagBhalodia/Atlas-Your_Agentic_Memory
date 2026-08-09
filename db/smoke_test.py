"""ATLAS — Track A Day-1 smoke test.

Goal (TRACK_A §6, Day 1): prove the CockroachDB path end-to-end, independent of
AWS/Bedrock. This does NOT touch any embedding provider — it uses a dummy vector of
the correct length so a failure here can only mean a DB problem, never an API one.

What it does:
  1. Connects using COCKROACH_DATABASE_URL from .env
  2. Applies db/schema.sql (idempotent — safe to re-run)
  3. Inserts one `decisions` row + its matching `memory_index` row in ONE transaction
  4. Reads both back and prints them
  5. Cleans up the rows it created (leaves the tables in place)

Run:  ./.venv/bin/python db/smoke_test.py
"""
import pathlib

from psycopg2.extras import RealDictCursor

from connection import get_conn

EMBED_DIM = 1536  # must match VECTOR(...) in db/schema.sql
SCHEMA_PATH = pathlib.Path(__file__).with_name("schema.sql")


def vec_literal(values) -> str:
    """pgvector text literal, e.g. '[0.1,0.2,...]' — how a VECTOR is passed as a param."""
    return "[" + ",".join(str(v) for v in values) + "]"


def main() -> None:
    print("Connecting to CockroachDB...")
    conn = get_conn()
    conn.autocommit = False
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 1) schema (idempotent)
            print("Applying schema.sql...")
            cur.execute(SCHEMA_PATH.read_text())

            # 2) insert a decision + its index row, atomically
            print("Inserting test decision + memory_index row...")
            cur.execute(
                """
                INSERT INTO decisions
                    (topic, old_state, new_state, cause, trigger_event, tension, recorded_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (
                    "mobile offline sync",
                    "shipping in Q3",
                    "deprioritized to Q4",
                    "SSO work ate the sprint",
                    "enterprise deal required SSO",
                    "offline UX vs. enterprise revenue",
                    "smoke_test",
                ),
            )
            decision_id = cur.fetchone()["id"]

            dummy_vec = vec_literal([0.001 * (i % 100) for i in range(EMBED_DIM)])
            cur.execute(
                """
                INSERT INTO memory_index
                    (topic, decision_id, tag, tag_embedding, sequence_num)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
                """,
                ("mobile offline sync", decision_id, "deprioritized for SSO bandwidth",
                 dummy_vec, 1),
            )
            index_id = cur.fetchone()["id"]
            conn.commit()
            print(f"  decision id     = {decision_id}")
            print(f"  memory_index id = {index_id}")

            # 3) read back via a join, proving the pointer resolves
            cur.execute(
                """
                SELECT d.topic, d.old_state, d.new_state, d.cause,
                       m.tag, m.sequence_num,
                       vector_dims(m.tag_embedding) AS dims
                FROM memory_index m
                JOIN decisions d ON d.id = m.decision_id
                WHERE m.id = %s;
                """,
                (index_id,),
            )
            row = cur.fetchone()
            print("\nRead back:")
            for k, v in row.items():
                print(f"  {k:12} = {v}")
            assert row["dims"] == EMBED_DIM, f"stored dim {row['dims']} != {EMBED_DIM}"

            # 4) cleanup (child first — FK)
            cur.execute("DELETE FROM memory_index WHERE id = %s;", (index_id,))
            cur.execute("DELETE FROM decisions WHERE id = %s;", (decision_id,))
            conn.commit()
            print("\nCleaned up test rows.")

        print("\nPASS — CockroachDB path works end-to-end (connect → schema → "
              "insert → join read-back → delete).")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
