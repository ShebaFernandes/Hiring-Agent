"""
One-off seed script: creates 10 sample jobs so the apply page dropdown and
the admin dashboard have data to show immediately.

Note: the app also auto-seeds on startup when the DB is empty (see
app/seed_data.py), so running this by hand is only needed if you want to
force a reset.

Usage:
    python seed.py            # skip if jobs already exist
    python seed.py --force    # wipe jobs + candidates and reseed
"""
import sqlite3
import sys

from app.config import Config
from app.extensions import SCHEMA
from app.seed_data import SAMPLE_JOBS, _insert_sample_jobs


def seed(force=False):
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.executescript(SCHEMA)

    existing = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    if existing > 0 and not force:
        print(f"Skipping seed: {existing} job(s) already exist. Use --force to reset.")
        conn.close()
        return

    if force:
        conn.execute("DELETE FROM candidates")
        conn.execute("DELETE FROM jobs")
        print("Cleared existing jobs and candidates.")

    _insert_sample_jobs(conn)
    conn.close()
    print(f"Seeded {len(SAMPLE_JOBS)} jobs into '{Config.DATABASE_PATH}'.")


if __name__ == "__main__":
    seed(force="--force" in sys.argv)
