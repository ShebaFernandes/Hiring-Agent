from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from pymongo import ReturnDocument

from ..extensions import get_db
from ..utils.serializers import serialize_job

job_bp = Blueprint("jobs", __name__)


@job_bp.get("/jobs")
def list_jobs_public():
    """Public endpoint - powers the job dropdown on the apply page. No auth."""
    db = get_db()
    jobs = db.jobs.find().sort("created_at", -1)
    return jsonify([serialize_job(j) for j in jobs])


@job_bp.get("/admin/jobs")
@jwt_required()
def list_jobs_admin():
    db = get_db()
    jobs = db.jobs.find().sort("created_at", -1)
    return jsonify([serialize_job(j) for j in jobs])


@job_bp.post("/admin/jobs")
@jwt_required()
def create_job():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "Title is required"}), 400

    doc = {
        "title": title,
        "department": (data.get("department") or "").strip(),
        "location": (data.get("location") or "").strip(),
        "job_type": (data.get("job_type") or "Full-time").strip(),
        "description": (data.get("description") or "").strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    db = get_db()
    result = db.jobs.insert_one(doc)
    doc["_id"] = result.inserted_id
    return jsonify(serialize_job(doc)), 201


@job_bp.put("/admin/jobs/<job_id>")
@jwt_required()
def update_job(job_id):
    try:
        oid = ObjectId(job_id)
    except InvalidId:
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
    updated = db.jobs.find_one_and_update(
        {"_id": oid}, {"$set": updates}, return_document=ReturnDocument.AFTER
    )
    if not updated:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(serialize_job(updated))


@job_bp.delete("/admin/jobs/<job_id>")
@jwt_required()
def delete_job(job_id):
    try:
        oid = ObjectId(job_id)
    except InvalidId:
        return jsonify({"error": "Invalid job id"}), 400

    db = get_db()
    result = db.jobs.delete_one({"_id": oid})
    if result.deleted_count == 0:
        return jsonify({"error": "Job not found"}), 404

    # Deliberately not cascading to candidates: existing applications for a
    # deleted job should stay visible in the dashboard for record-keeping.
    return jsonify({"success": True})
