"""
sqlite3.Row objects support dict-style [] access but not .get(), and IDs are
plain integers - these helpers normalize a row into the JSON shape the
frontend expects (string ids) before it goes into a jsonify() response.
"""


def serialize_job(job):
    return {
        "id": str(job["id"]),
        "title": job["title"],
        "department": job["department"],
        "location": job["location"],
        "job_type": job["job_type"],
        "description": job["description"],
        "created_at": job["created_at"],
    }


def serialize_candidate(candidate):
    return {
        "id": str(candidate["id"]),
        "name": candidate["name"],
        "phone": candidate["phone"],
        "email": candidate["email"],
        "job_id": str(candidate["job_id"]),
        "job_title": candidate["job_title"],
        "note": candidate["note"],
        "resume_filename": candidate["resume_filename"],
        "resume_original_name": candidate["resume_original_name"],
        "stage": candidate["stage"],
        "applied_at": candidate["applied_at"],
    }
