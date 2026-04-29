def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_readiness_check(client):
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_request_id_header(client):
    response = client.get("/health", headers={"X-Request-ID": "test-request-id"})

    assert response.headers["X-Request-ID"] == "test-request-id"


def test_local_upload_disabled_in_production_path(client, auth_headers):
    response = client.post(
        "/api/uploads/local",
        headers=auth_headers,
        files={"file": ("test.png", b"not-really-an-image", "image/png")},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Local uploads are disabled"
