"""Tests for authentication endpoints."""


def test_register_user_success(client):
    """Test successful user registration."""
    response = client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "SecurePass123!",
        "first_name": "New",
        "last_name": "User"
    })
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == "newuser@example.com"
    assert data["first_name"] == "New"
    assert "password" not in data


def test_register_duplicate_email(client, test_user):
    """Test registration with duplicate email."""
    response = client.post("/api/v1/auth/register", json={
        "email": test_user.email,
        "password": "password123",
        "first_name": "Duplicate"
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client, test_user):
    """Test login with invalid password."""
    response = client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_invalid_email(client):
    """Test login with non-existent email."""
    response = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "password123"
    })
    assert response.status_code == 401


def test_get_current_user(client, test_user, auth_headers):
    """Test getting current user info."""
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert str(data["id"]) == str(test_user.id)


def test_get_current_user_without_auth(client):
    """Test accessing protected endpoint without authentication."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 403  # FastAPI HTTPBearer returns 403
