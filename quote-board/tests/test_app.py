import pytest

from app import app


@pytest.fixture
def client():
    app.testing = True
    return app.test_client()


def test_list_quotes_returns_seed_data(client):
    resp = client.get("/quotes")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 3


def test_get_quote_by_id(client):
    resp = client.get("/quotes/1")
    assert resp.status_code == 200
    assert resp.get_json()["author"] == "Leonardo da Vinci"


def test_get_missing_quote_returns_404(client):
    resp = client.get("/quotes/999")
    assert resp.status_code == 404


def test_create_quote(client):
    resp = client.post("/quotes", json={"text": "Test", "author": "Tester"})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["likes"] == 0


def test_like_quote_increments_and_persists(client):
    resp = client.post("/quotes/1/like")
    assert resp.status_code == 200
    assert resp.get_json()["likes"] == 1

    resp = client.get("/quotes/1")
    assert resp.get_json()["likes"] == 1


def test_unlike_quote_decrements_and_persists(client):
    client.post("/quotes/2/like")
    client.post("/quotes/2/like")

    resp = client.post("/quotes/2/unlike")
    assert resp.status_code == 200
    assert resp.get_json()["likes"] == 1

    resp = client.get("/quotes/2")
    assert resp.get_json()["likes"] == 1


def test_unlike_quote_floors_at_zero(client):
    resp = client.post("/quotes/3/unlike")
    assert resp.status_code == 200
    assert resp.get_json()["likes"] == 0

    resp = client.get("/quotes/3")
    assert resp.get_json()["likes"] == 0


def test_like_and_unlike_missing_quote_return_404(client):
    assert client.post("/quotes/999/like").status_code == 404
    assert client.post("/quotes/999/unlike").status_code == 404
