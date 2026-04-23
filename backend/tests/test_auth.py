import pytest
from app.models import User


def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "business_name": "New Business"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "id" in data


def test_register_duplicate_user(client, test_user):
    """Test registration with duplicate username"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "another@example.com",
            "username": "testuser",
            "password": "password123"
        }
    )
    
    assert response.status_code == 400


def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    """Test login with wrong password"""
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    
    assert response.status_code == 401


def test_get_current_user(client, auth_headers):
    """Test getting current user information"""
    response = client.get("/api/auth/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
