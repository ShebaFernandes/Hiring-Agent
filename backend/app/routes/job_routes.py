from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ..extensions import get_db
from ..utils.serializers import serialize_job

job_bp = Blueprint("jobs", __name__)


def _parse_job_id(job_id):
    try:
        return int(job_id)
    except (TypeError, ValueError):
        return None


@job_bp.get("/jobs")
def list_jobs_public():
    """Public endpoint - powers the job dropdown on the apply page. No auth."""
    db = get_db()
    jobs = db.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()
    return jsonify([serialize_job(j) for j in jobs])


@job_bp.get("/admin/jobs")
@jwt_required()
def list_jobs_admin():
    db = get_db()
    jobs = db.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()
    return jsonify([serialize_job(j) for j in jobs])


@job_bp.post("/admin/jobs")
@jwt_required()
def create_job():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "Title is required"}), 400

    fields = {
        "title": title,
        "department": (data.get("department") or "").strip(),
        "location": (data.get("location") or "").strip(),
        "job_type": (data.get("job_type") or "Full-time").strip(),
        "description": (data.get("description") or "").strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    db = get_db()
    cursor = db.execute(
        """INSERT INTO jobs (title, department, location, job_type, description, created_at)
           VALUES (:title, :department, :location, :job_type, :description, :created_at)""",
        fields,
    )
    db.commit()
    job = db.execute("SELECT * FROM jobs WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return jsonify(serialize_job(job)), 201


@job_bp.put("/admin/jobs/<job_id>")
@jwt_required()
def update_job(job_id):
    job_pk = _parse_job_id(job_id)
    if job_pk is None:
        return jsonify({"error": "Invalid job id"}), 400

    data = request.get_json(silent=True) or {}
    updates = {}
    for field in ("title", "department", "location", "job_type", "description"):
        if field in data:
            updates[field] = (data[field] or "").strip()

    if not updates:
        return jsonify({"error": "No fields to update"}), 400
    if "title" in updates and not updates["title"]:
        return jsonify({"error": "Title cannot be empty"}), 400

    db = get_db()
    set_clause = ", ".join(f"{field} = :{field}" for field in updates)
    updates["job_id"] = job_pk
    result = db.execute(f"UPDATE jobs SET {set_clause} WHERE id = :job_id", updates)
    db.commit()
    if result.rowcount == 0:
        return jsonify({"error": "Job not found"}), 404

    job = db.execute("SELECT * FROM jobs WHERE id = ?", (job_pk,)).fetchone()
    return jsonify(serialize_job(job))


@job_bp.delete("/admin/jobs/<job_id>")
@jwt_required()
def delete_job(job_id):
    job_pk = _parse_job_id(job_id)
    if job_pk is None:
        return jsonify({"error": "Invalid job id"}), 400

    db = get_db()
    result = db.execute("DELETE FROM jobs WHERE id = ?", (job_pk,))
    db.commit()
    if result.rowcount == 0:
        return jsonify({"error": "Job not found"}), 404

    # Deliberately not cascading to candidates: existing applications for a
    # deleted job should stay visible in the dashboard for record-keeping.
    return jsonify({"success": True})
