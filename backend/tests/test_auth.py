def test_get_current_user(client, auth_headers):
    """Test getting current Clerk-authenticated user information."""
    response = client.get("/api/auth/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["clerk_user_id"] == "user_test"


def test_get_current_user_requires_auth(client):
    """Test protected auth route without credentials."""
    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_update_current_user(client, auth_headers):
    """Test updating the Clerk-backed user profile."""
    response = client.patch(
        "/api/auth/me",
        headers=auth_headers,
        json={"business_name": "Updated Business", "bank_name": "Test Bank"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["business_name"] == "Updated Business"
    assert data["bank_name"] == "Test Bank"


def test_auth_status(client):
    """Test authentication service status endpoint."""
    response = client.get("/api/auth/status")

    assert response.status_code == 200
    assert response.json()["auth_provider"] == "clerk"
