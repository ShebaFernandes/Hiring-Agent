"""
Shared extension instances, initialized once and imported by routes.

`_db` is set inside init_mongo() when the app factory runs. Routes must call
get_db() (not import `_db` directly) because Python binds imported names to
the value that existed at import time - if a route did
`from app.extensions import _db` at module load, it would capture `None`
forever, since init_mongo() hasn't run yet at that point.
"""
from flask_jwt_extended import JWTManager
from pymongo import MongoClient

jwt = JWTManager()

_client = None
_db = None


def init_mongo(app):
    global _client, _db
    _client = MongoClient(app.config["MONGO_URI"])
    _db = _client[app.config["MONGO_DBNAME"]]
    return _db


def get_db():
    if _db is None:
        raise RuntimeError("Mongo has not been initialized - call init_mongo(app) first.")
    return _db
