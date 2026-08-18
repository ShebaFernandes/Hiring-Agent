import os
import uuid
from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, current_app, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required
from pymongo import ReturnDocument
from werkzeug.utils import secure_filename

from ..constants import ALLOWED_RESUME_EXTENSIONS, STAGES
from ..extensions import get_db
from ..utils.serializers import serialize_candidate

candidate_bp = Blueprint("candidates", __name__)


def _allowed_resume(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_RESUME_EXTENSIONS
    )


@candidate_bp.post("/apply")
def apply():
    """Public endpoint the candidate-facing form submits to.

    multipart/form-data because a file (resume) rides alongside plain text
    fields - JSON bodies can't carry binary file content.
    """
    form = request.form
    name = (form.get("name") or "").strip()
    phone = (form.get("phone") or "").strip()
    email = (form.get("email") or "").strip()
    job_id = (form.get("job_id") or "").strip()
    note = (form.get("note") or "").strip()

    if not all([name, phone, email, job_id]):
        return jsonify({"error": "Name, phone, email and job are required"}), 400

    try:
        job_oid = ObjectId(job_id)
    except InvalidId:
        return jsonify({"error": "Invalid job selected"}), 400

    db = get_db()
    job = db.jobs.find_one({"_id": job_oid})
    if not job:
        return jsonify({"error": "Selected job does not exist"}), 404

    resume = request.files.get("resume")
    if not resume or resume.filename == "":
        return jsonify({"error": "Resume is required"}), 400
    if not _allowed_resume(resume.filename):
        return jsonify({"error": "Resume must be a PDF or Word document"}), 400

    # Prefix with a uuid so two candidates uploading "resume.pdf" never
    # collide or overwrite each other on disk.
    safe_name = secure_filename(resume.filename)
    stored_filename = f"{uuid.uuid4().hex}_{safe_name}"
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    resume.save(os.path.join(upload_dir, stored_filename))

    doc = {
        "name": name,
        "phone": phone,
        "email": email,
        "job_id": job_oid,
        "job_title": job["title"],
        "note": note,
        "resume_filename": stored_filename,
        "resume_original_name": safe_name,
        "stage": "Applied",
        "applied_at": datetime.now(timezone.utc).isoformat(),
    }
    result = db.candidates.insert_one(doc)
    doc["_id"] = result.inserted_id
    return jsonify(serialize_candidate(doc)), 201


@candidate_bp.get("/admin/candidates")
@jwt_required()
def list_candidates():
    """Supports optional ?job_id=...&stage=... filters used by the dashboard."""
    db = get_db()
    query = {}

    job_id = request.args.get("job_id")
    if job_id:
        try:
            query["job_id"] = ObjectId(job_id)
        except InvalidId:
            return jsonify({"error": "Invalid job id"}), 400

    stage = request.args.get("stage")
    if stage:
        if stage not in STAGES:
            return jsonify({"error": f"Invalid stage. Must be one of {STAGES}"}), 400
        query["stage"] = stage

    candidates = db.candidates.find(query).sort("applied_at", -1)
    return jsonify([serialize_candidate(c) for c in candidates])


@candidate_bp.patch("/admin/candidates/<candidate_id>/stage")
@jwt_required()
def update_stage(candidate_id):
    try:
        oid = ObjectId(candidate_id)
    except InvalidId:
        return jsonify({"error": "Invalid candidate id"}), 400

    data = request.get_json(silent=True) or {}
    stage = data.get("stage")
    if stage not in STAGES:
        return jsonify({"error": f"Stage must be one of {STAGES}"}), 400

    db = get_db()
    updated = db.candidates.find_one_and_update(
        {"_id": oid}, {"$set": {"stage": stage}}, return_document=ReturnDocument.AFTER
    )
    if not updated:
        return jsonify({"error": "Candidate not found"}), 404
    return jsonify(serialize_candidate(updated))


@candidate_bp.get("/admin/candidates/<candidate_id>/resume")
@jwt_required()
def download_resume(candidate_id):
    try:
        oid = ObjectId(candidate_id)
    except InvalidId:
        return jsonify({"error": "Invalid candidate id"}), 400

    db = get_db()
    candidate = db.candidates.find_one({"_id": oid})
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(
        upload_dir,
        candidate["resume_filename"],
        as_attachment=True,
        download_name=candidate.get("resume_original_name") or "resume",
    )


@candidate_bp.get("/stages")
def list_stages():
    """Lets the frontend fetch the canonical stage list instead of duplicating it."""
    return jsonify(STAGES)
