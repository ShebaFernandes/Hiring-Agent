import os

from flask import Flask, send_from_directory
from flask_cors import CORS

from .config import Config
from .extensions import close_db, init_db, jwt
from .seed_data import ensure_seed


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Allow the Vite dev server (and any other origin, since this is a
    # take-home project, not something with real users) to call the API.
    # In production the frontend is served from the same origin so CORS is
    # a no-op there, but it keeps the dev workflow simple.
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    jwt.init_app(app)
    init_db(app)
    app.teardown_appcontext(close_db)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Populate the 10 sample jobs on startup if the DB is empty, so the apply
    # page and dashboard are never blank on a fresh or reset database.
    ensure_seed(app.config["DATABASE_PATH"])

    from .routes.auth_routes import auth_bp
    from .routes.job_routes import job_bp
    from .routes.candidate_routes import candidate_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(job_bp, url_prefix="/api")
    app.register_blueprint(candidate_bp, url_prefix="/api")

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    # --- Serve the built React app (single-service deployment) ---------------
    # Any non-/api path returns a static file from frontend/dist if it exists,
    # otherwise index.html so React Router can handle client-side routes like
    # /admin. API routes are matched first (they're more specific), so this
    # catch-all never shadows them.
    @app.get("/", defaults={"path": ""})
    @app.get("/<path:path>")
    def serve_frontend(path):
        dist = app.config["FRONTEND_DIST"]
        if path.startswith("api/"):
            return {"error": "Not found"}, 404
        if path and os.path.exists(os.path.join(dist, path)):
            return send_from_directory(dist, path)
        index_path = os.path.join(dist, "index.html")
        if os.path.exists(index_path):
            return send_from_directory(dist, "index.html")
        return {
            "error": "Frontend not built. Run `npm run build` in frontend/ "
            "(the Docker image does this automatically)."
        }, 404

    return app
