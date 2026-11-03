import pytest

from app import create_app


@pytest.fixture
def database_url(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("SECRET_KEY", "test")
    monkeypatch.delenv("FRONTEND_DIST", raising=False)
    return url


@pytest.fixture
def client(database_url):
    return create_app().test_client()
