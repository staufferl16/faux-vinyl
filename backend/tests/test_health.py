from app import create_app


def test_health_reports_wal(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "database": "ok",
        "journal_mode": "wal",
    }


def test_health_returns_503_when_database_is_unavailable(database_url, monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'missing' / 'test.db'}")

    response = create_app().test_client().get("/api/health")

    assert response.status_code == 503
    assert response.get_json()["status"] == "error"
