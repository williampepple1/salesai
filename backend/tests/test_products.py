import pytest


def test_create_product(client, auth_headers):
    """Test creating a product"""
    response = client.post(
        "/api/products",
        headers=auth_headers,
        json={
            "name": "Test Product",
            "description": "A test product",
            "price": 99.99,
            "currency": "USD",
            "stock_quantity": 10,
            "is_available": True,
            "image_urls": []
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["price"] == 99.99
    assert "id" in data


def test_get_products(client, auth_headers):
    """Test getting all products"""
    # Create a product first
    client.post(
        "/api/products",
        headers=auth_headers,
        json={
            "name": "Test Product",
            "price": 50.00,
            "stock_quantity": 5
        }
    )
    
    response = client.get("/api/products", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Test Product"


def test_get_product_by_id(client, auth_headers):
    """Test getting a specific product"""
    # Create a product
    create_response = client.post(
        "/api/products",
        headers=auth_headers,
        json={
            "name": "Specific Product",
            "price": 75.00,
            "stock_quantity": 3
        }
    )
    product_id = create_response.json()["id"]
    
    # Get the product
    response = client.get(f"/api/products/{product_id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == "Specific Product"


def test_update_product(client, auth_headers):
    """Test updating a product"""
    # Create a product
    create_response = client.post(
        "/api/products",
        headers=auth_headers,
        json={
            "name": "Original Name",
            "price": 100.00,
            "stock_quantity": 5
        }
    )
    product_id = create_response.json()["id"]
    
    # Update the product
    response = client.put(
        f"/api/products/{product_id}",
        headers=auth_headers,
        json={
            "name": "Updated Name",
            "price": 120.00
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["price"] == 120.00


def test_delete_product(client, auth_headers):
    """Test deleting a product"""
    # Create a product
    create_response = client.post(
        "/api/products",
        headers=auth_headers,
        json={
            "name": "To Be Deleted",
            "price": 50.00,
            "stock_quantity": 1
        }
    )
    product_id = create_response.json()["id"]
    
    # Delete the product
    response = client.delete(f"/api/products/{product_id}", headers=auth_headers)
    
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/products/{product_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_unauthorized_access(client):
    """Test accessing products without authentication"""
    response = client.get("/api/products")
    assert response.status_code == 401
