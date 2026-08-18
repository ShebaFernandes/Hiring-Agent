"""
One-off seed script: creates 10 sample jobs so the apply page dropdown and
the admin dashboard have data to show immediately.

Usage:
    python seed.py            # skip if jobs already exist
    python seed.py --force    # wipe jobs + candidates and reseed
"""
import sys
from datetime import datetime, timezone

from pymongo import MongoClient

from app.config import Config

SAMPLE_JOBS = [
    {"title": "Frontend Engineer", "department": "Engineering", "location": "Bangalore", "job_type": "Full-time", "description": "Build and maintain our React-based product UI."},
    {"title": "Backend Engineer", "department": "Engineering", "location": "Remote", "job_type": "Full-time", "description": "Design and scale our Flask/MongoDB APIs."},
    {"title": "Product Designer", "department": "Design", "location": "Mumbai", "job_type": "Full-time", "description": "Own end-to-end product design from research to polish."},
    {"title": "Data Analyst", "department": "Data", "location": "Remote", "job_type": "Full-time", "description": "Turn raw data into actionable business insights."},
    {"title": "DevOps Engineer", "department": "Engineering", "location": "Pune", "job_type": "Full-time", "description": "Own CI/CD pipelines and cloud infrastructure."},
    {"title": "QA Engineer", "department": "Engineering", "location": "Hyderabad", "job_type": "Full-time", "description": "Build automated test suites and ensure release quality."},
    {"title": "Marketing Intern", "department": "Marketing", "location": "Remote", "job_type": "Internship", "description": "Support campaigns across social and content channels."},
    {"title": "HR Executive", "department": "People", "location": "Delhi", "job_type": "Full-time", "description": "Manage recruitment coordination and employee onboarding."},
    {"title": "Sales Development Rep", "department": "Sales", "location": "Bangalore", "job_type": "Full-time", "description": "Generate and qualify new business leads."},
    {"title": "AI/ML Intern", "department": "Engineering", "location": "Remote", "job_type": "Internship", "description": "Prototype ML models for candidate screening and matching."},
]


def seed(force=False):
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.MONGO_DBNAME]

    existing = db.jobs.count_documents({})
    if existing > 0 and not force:
        print(f"Skipping seed: {existing} job(s) already exist. Use --force to reset.")
        return

    if force:
        db.jobs.delete_many({})
        db.candidates.delete_many({})
        print("Cleared existing jobs and candidates.")

    now = datetime.now(timezone.utc).isoformat()
    for job in SAMPLE_JOBS:
        job["created_at"] = now
    db.jobs.insert_many(SAMPLE_JOBS)
    print(f"Seeded {len(SAMPLE_JOBS)} jobs into '{Config.MONGO_DBNAME}'.")


if __name__ == "__main__":
    seed(force="--force" in sys.argv)
