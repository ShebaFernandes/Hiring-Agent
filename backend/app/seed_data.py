"""
Sample jobs and a helper to auto-populate them.

Both the standalone `seed.py` script and the app's startup path import from
here so the 10 sample jobs are defined in exactly one place. `ensure_seed` is
called on every app startup: it only inserts jobs when the table is empty, so
it's safe to run repeatedly and guarantees the apply-page dropdown and the
admin dashboard are never blank on a fresh (or reset) database.
"""
import sqlite3
from datetime import datetime, timezone

from .extensions import SCHEMA

SAMPLE_JOBS = [
    {"title": "Frontend Engineer", "department": "Engineering", "location": "Bangalore", "job_type": "Full-time", "description": "Build and maintain our React-based product UI."},
    {"title": "Backend Engineer", "department": "Engineering", "location": "Remote", "job_type": "Full-time", "description": "Design and scale our Flask/SQLite APIs."},
    {"title": "Product Designer", "department": "Design", "location": "Mumbai", "job_type": "Full-time", "description": "Own end-to-end product design from research to polish."},
    {"title": "Data Analyst", "department": "Data", "location": "Remote", "job_type": "Full-time", "description": "Turn raw data into actionable business insights."},
    {"title": "DevOps Engineer", "department": "Engineering", "location": "Pune", "job_type": "Full-time", "description": "Own CI/CD pipelines and cloud infrastructure."},
    {"title": "QA Engineer", "department": "Engineering", "location": "Hyderabad", "job_type": "Full-time", "description": "Build automated test suites and ensure release quality."},
    {"title": "Marketing Intern", "department": "Marketing", "location": "Remote", "job_type": "Internship", "description": "Support campaigns across social and content channels."},
    {"title": "HR Executive", "department": "People", "location": "Delhi", "job_type": "Full-time", "description": "Manage recruitment coordination and employee onboarding."},
    {"title": "Sales Development Rep", "department": "Sales", "location": "Bangalore", "job_type": "Full-time", "description": "Generate and qualify new business leads."},
    {"title": "AI/ML Intern", "department": "Engineering", "location": "Remote", "job_type": "Internship", "description": "Prototype ML models for candidate screening and matching."},
]

_INSERT = """INSERT INTO jobs (title, department, location, job_type, description, created_at)
             VALUES (:title, :department, :location, :job_type, :description, :created_at)"""


def _insert_sample_jobs(conn):
    now = datetime.now(timezone.utc).isoformat()
    rows = [{**job, "created_at": now} for job in SAMPLE_JOBS]
    conn.executemany(_INSERT, rows)
    conn.commit()


def ensure_seed(database_path):
    """Insert the sample jobs only if the jobs table is currently empty.

    Called on app startup so a freshly created (or reset) database always has
    jobs to show. A no-op once jobs exist.
    """
    conn = sqlite3.connect(database_path)
    try:
        conn.executescript(SCHEMA)
        count = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        if count == 0:
            _insert_sample_jobs(conn)
            return len(SAMPLE_JOBS)
        return 0
    finally:
        conn.close()
