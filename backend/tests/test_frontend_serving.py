import pytest

from app import create_app


@pytest.fixture
def prod_client(database_url, monkeypatch, tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<h1>index</h1>")
    (dist / "app.js").write_text("console.log('app')")
    (tmp_path / "secret.txt").write_text("secret")
    monkeypatch.setenv("FRONTEND_DIST", str(dist))
    return create_app().test_client()


def test_serves_index_and_assets(prod_client):
    assert b"index" in prod_client.get("/").data
    assert b"console.log" in prod_client.get("/app.js").data


def test_client_side_routes_fall_back_to_index(prod_client):
    assert b"index" in prod_client.get("/some/page").data


def test_unknown_api_routes_are_not_served_the_ui(prod_client):
    assert prod_client.get("/api/nope").status_code == 404
    assert prod_client.get("/auth/nope").status_code == 404


def test_cannot_read_outside_dist(prod_client):
    assert b"secret" not in prod_client.get("/../secret.txt").data
