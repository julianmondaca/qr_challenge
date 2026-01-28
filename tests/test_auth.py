import pytest
from fastapi import status

def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "uuid" in data

def test_register_duplicate_email(client):
    # First registration
    client.post(
        "/api/v1/auth/register",
        json={"email": "duplicate@example.com", "password": "password123"}
    )
    # Second registration with same email
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "duplicate@example.com", "password": "password123"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already registered"

def test_login_success(client):
    # Register first
    email = "login@example.com"
    password = "password123"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password}
    )
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    email = "wrong@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "correctpassword"}
    )
    
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
