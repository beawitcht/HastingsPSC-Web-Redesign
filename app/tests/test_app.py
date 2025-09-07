import pytest

def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hastings & District Palestine Solidarity Campaign" in response.data

def test_article_route_success(client):
    response = client.get("/articles/Hastings_Three_Found_Not_Guilty_In_Case_Against_General_Dynamics")
    assert response.status_code == 200
    assert b"Hastings Three Found Not Guilty In Case Against General Dynamics" in response.data

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
