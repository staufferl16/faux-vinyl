from pathlib import Path

from flask import Blueprint, abort, current_app, jsonify, send_from_directory
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

api = Blueprint("api", __name__, url_prefix="/api")


@api.get("/health")
def health():
    engine = current_app.extensions["db_engine"]
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            journal_mode = None
            if engine.dialect.name == "sqlite":
                journal_mode = connection.execute(text("PRAGMA journal_mode")).scalar()
    except SQLAlchemyError:
        current_app.logger.exception("Database health check failed")
        return jsonify(status="error", database="unavailable"), 503

    return jsonify(status="ok", database="ok", journal_mode=journal_mode)


def frontend_blueprint(dist):
    dist = Path(dist).resolve()
    frontend = Blueprint("frontend", __name__)

    @frontend.get("/", defaults={"path": ""})
    @frontend.get("/<path:path>")
    def serve(path):
        # Unknown API routes should 404, not return the UI.
        if path == "api" or path.startswith(("api/", "auth/")):
            abort(404)
        if path and (dist / path).is_file():
            return send_from_directory(dist, path)
        return send_from_directory(dist, "index.html")

    return frontend
