import os

from flask import Flask
from flask_cors import CORS

from .config import Config
from .extensions import close_db, init_db, jwt


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Allow the Vite dev server (and any other origin, since this is a
    # take-home project, not something with real users) to call the API.
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    jwt.init_app(app)
    init_db(app)
    app.teardown_appcontext(close_db)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    from .routes.auth_routes import auth_bp
    from .routes.job_routes import job_bp
    from .routes.candidate_routes import candidate_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(job_bp, url_prefix="/api")
    app.register_blueprint(candidate_bp, url_prefix="/api")

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app
