import os


def secret_key():
    key = os.environ.get("SECRET_KEY")
    if not key:
        raise RuntimeError("SECRET_KEY must be set")
    return key


def database_url():
    return os.environ.get("DATABASE_URL", "sqlite:///app.db")


def frontend_dist():
    return os.environ.get("FRONTEND_DIST")
