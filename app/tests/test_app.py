import pytest

def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hastings & District Palestine Solidarity Campaign" in response.data

def test_article_route_success(client):
    response = client.get("/articles/test-article")
    assert response.status_code == 200
    assert b"COUNCIL LEADER SLAMS ISRAEL'S 'INHUMANE' ATTACK ON AL MAWASI" in response.data

def test_article_route_not_found(client):
    response = client.get("/articles/nonexistent-article")
    assert response.status_code == 404

def test_csp_header(client):
    response = client.get("/")
    csp = response.headers.get("Content-Security-Policy")
    assert csp is not None
    assert "default-src" in csp

def test_footer_present(client):
    response = client.get("/")
    assert b"Knowledge belongs to all without limits" in response.data
