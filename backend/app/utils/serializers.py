"""
Mongo documents use ObjectId and are not JSON-serializable as-is.
These helpers convert a raw document into a plain dict of JSON-safe values
before it goes into a jsonify() response.
"""


def serialize_job(job):
    return {
        "id": str(job["_id"]),
        "title": job.get("title", ""),
        "department": job.get("department", ""),
        "location": job.get("location", ""),
        "job_type": job.get("job_type", ""),
        "description": job.get("description", ""),
        "created_at": job.get("created_at"),
    }


def serialize_candidate(candidate):
    return {
        "id": str(candidate["_id"]),
        "name": candidate.get("name", ""),
        "phone": candidate.get("phone", ""),
        "email": candidate.get("email", ""),
        "job_id": str(candidate["job_id"]),
        "job_title": candidate.get("job_title", ""),
        "note": candidate.get("note", ""),
        "resume_filename": candidate.get("resume_filename"),
        "resume_original_name": candidate.get("resume_original_name"),
        "stage": candidate.get("stage", "Applied"),
        "applied_at": candidate.get("applied_at"),
    }
