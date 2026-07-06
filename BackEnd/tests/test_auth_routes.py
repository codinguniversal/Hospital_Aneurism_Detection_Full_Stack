"""
Tests for authentication routes: POST /auth/login, POST /auth/register, GET /auth/check-email
"""
import pytest
from fastapi import status
from app.main import app  
from app.api.v1.dependencies.auth import get_current_user_claims
from app.modules.identity_access.entities import UserEntity


class TestEmailCheckRoute:
    """Tests for GET /auth/check-email endpoint."""

    @pytest.fixture(autouse=True)
    def setup_admin_rbac_claims(self):
        """
        Repeat the RBAC procedure: Override the default Radiologist claims
        with Admin claims specifically for this admin-restricted router suite.
        """
        # inject an Admin role to satisfy Depends(RoleChecker(["admin"]))
        app.dependency_overrides[get_current_user_claims] = lambda: {
            "sub": "admin@hospital.com", 
            "role": "admin", 
            "employee_id": "ADM-001"
        }
        yield
        # clean up and reset back to standard default context
        app.dependency_overrides[get_current_user_claims] = lambda: {
            "sub": "test@test.com", 
            "role": "Radiologist", 
            "employee_id": "EMP-12345"
        }

    def test_check_email_available(self, client, stub_check_email):
        """Should return 200 with exists=False when email is not registered."""
        stub_check_email.exists = False

        response = client.get("/auth/check-email?email=newuser@example.com")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"exists": False}

    def test_check_email_exists(self, client, stub_check_email):
        """Should return 200 with exists=True when email is registered."""
        stub_check_email.exists = True

        response = client.get("/auth/check-email?email=existing@example.com")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"exists": True}


class TestLoginRoute:
    """Tests for POST /auth/login endpoint."""

    def test_login_success(self, client, stub_auth):
        """Should return 200 with user details on valid credentials."""
        stub_auth.user = UserEntity(
            employee_id="EMP-001",
            email="test@example.com",
            password="secret123",
            role="Radiologist"
        )

        response = client.post(
            "/auth/login",
            json={
                "loginIdentifier": "test@example.com",
                "password": "secret123",
                "isAdmin": False
            }
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == "test@example.com"
        assert response.json()["role"] == "Radiologist"

    def test_login_invalid_credentials(self, client, stub_auth):
        """Should return 401 on invalid email/password combination."""
        stub_auth.user = UserEntity(
            employee_id="EMP-001",
            email="test@example.com",
            password="secret123",
            role="Radiologist"
        )

        response = client.post(
            "/auth/login",
            json={
                "loginIdentifier": "wrong@example.com",
                "password": "badpass",
                "isAdmin": False
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "invalid credentials or role selection"

    def test_login_with_employee_id(self, client, stub_auth):
        """Should allow login using employee_id as loginIdentifier."""
        stub_auth.user = UserEntity(
            employee_id="EMP-001",
            email="test@example.com",
            password="secret123",
            role="Radiologist"
        )

        response = client.post(
            "/auth/login",
            json={
                "loginIdentifier": "EMP-001",
                "password": "secret123",
                "isAdmin": False
            }
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["employee_id"] == "EMP-001"


class TestRegisterRoute:
    """Tests for POST /auth/register endpoint."""

    def test_register_success(self, client, stub_register):
        """Should return 201 with user_id on successful registration."""
        stub_register.users = []

        response = client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "password123",
                "gender": "female"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["status"] == "success"
        assert response.json()["user_id"] == "EMP-12345"

    def test_register_duplicate_email(self, client, stub_register):
        """Should return 400 when attempting to register with existing email."""
        stub_register.users = [
            UserEntity(
                employee_id="EMP-001",
                email="duplicate@example.com",
                password="password123",
                role="Radiologist"
            )
        ]

        response = client.post(
            "/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "password123",
                "gender": "female"
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    def test_register_multiple_users(self, client, stub_register):
        """Should support registering multiple different users."""
        stub_register.users = []

        # Register first user
        response1 = client.post(
            "/auth/register",
            json={
                "email": "user1@example.com",
                "password": "pass1",
                "gender": "male"
            }
        )
        assert response1.status_code == status.HTTP_201_CREATED

        # Register second user
        response2 = client.post(
            "/auth/register",
            json={
                "email": "user2@example.com",
                "password": "pass2",
                "gender": "female"
            }
        )
        assert response2.status_code == status.HTTP_201_CREATED
