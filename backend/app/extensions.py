"""
Shared extension instances, initialized once and imported by routes.

SQLite connections aren't safe to share across threads, so instead of one
global connection we open one per request via Flask's `g` and close it in
teardown_appcontext. Routes must call get_db() (not manage a connection
directly) to get that per-request connection.
"""
import os
import sqlite3

from flask import g
from flask_jwt_extended import JWTManager

jwt = JWTManager()

_database_path = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    department TEXT NOT NULL DEFAULT '',
    location TEXT NOT NULL DEFAULT '',
    job_type TEXT NOT NULL DEFAULT 'Full-time',
    description TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    job_id INTEGER NOT NULL REFERENCES jobs(id),
    job_title TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    resume_filename TEXT,
    resume_original_name TEXT,
    stage TEXT NOT NULL DEFAULT 'Applied',
    applied_at TEXT NOT NULL
);
"""


def init_db(app):
    global _database_path
    _database_path = app.config["DATABASE_PATH"]
    # Make sure the directory holding the DB file exists (e.g. a mounted
    # /data volume in production) before sqlite tries to create the file.
    db_dir = os.path.dirname(os.path.abspath(_database_path))
    os.makedirs(db_dir, exist_ok=True)
    with sqlite3.connect(_database_path) as conn:
        conn.executescript(SCHEMA)


def get_db():
    if _database_path is None:
        raise RuntimeError("SQLite has not been initialized - call init_db(app) first.")
    if "db" not in g:
        g.db = sqlite3.connect(_database_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
