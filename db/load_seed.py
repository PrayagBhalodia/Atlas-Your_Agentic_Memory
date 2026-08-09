"""ATLAS — Track A seed loader.

Truncates both tables and reloads db/seed_decisions.json from scratch (idempotent —
safe to re-run, and doubles as the Day-6 'reset memory' path). Each row is inserted via
the same _insert_decision() the live write-back uses, so loading exercises the real
dual-write + embedding path, not a special case.

Run:  ./.venv/bin/python db/load_seed.py
"""
import json
import pathlib

from connection import get_conn
from tools import _insert_decision

SEED_PATH = pathlib.Path(__file__).with_name("seed_decisions.json")


def main() -> None:
    records = json.loads(SEED_PATH.read_text())

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE decisions CASCADE;")  # also clears memory_index (FK)
        conn.commit()
    finally:
        conn.close()

    print(f"Cleared tables. Embedding + inserting {len(records)} decisions...")
    for i, rec in enumerate(records, 1):
        res = _insert_decision(
            topic=rec["topic"],
            old_state=rec.get("old_state"),
            new_state=rec["new_state"],
            cause=rec.get("cause"),
            trigger_event=rec.get("trigger_event"),
            tension=rec.get("tension"),
            recorded_by=rec["recorded_by"],
            tag=rec["tag"],
            sequence_num=rec.get("sequence_num"),
        )
        print(f"  [{i:2}/{len(records)}] {rec['topic']:22} #{rec.get('sequence_num')} "
              f"-> {res['id'][:8]}  ({rec['tag']})")

    print("\nDone. Seed data loaded.")


if __name__ == "__main__":
    main()
