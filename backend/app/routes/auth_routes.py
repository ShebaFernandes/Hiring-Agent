from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    """Single hardcoded admin login - no signup, per the assignment spec.

    Credentials are compared against ADMIN_EMAIL / ADMIN_PASSWORD from the
    environment (see backend/.env). On success we hand back a JWT the
    frontend stores and attaches as `Authorization: Bearer <token>` on every
    admin request.
    """
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if (
        email != current_app.config["ADMIN_EMAIL"].lower()
        or password != current_app.config["ADMIN_PASSWORD"]
    ):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=email)
    return jsonify({"token": token, "email": email})


@auth_bp.get("/me")
@jwt_required()
def me():
    """Lets the frontend check on load whether a stored token is still valid."""
    return jsonify({"email": get_jwt_identity()})
