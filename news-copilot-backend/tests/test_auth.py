import pytest
from http import HTTPStatus


class TestAuthEndpoints:
    def test_sign_up_success(self, client, session):
        response = client.post("/auth/sign-up", json={
            "email": "newuser@example.com",
            "password": "StrongPass123!",
            "confirmPassword": "StrongPass123!",
            "displayName": "New User",
            "acceptTerms": True,
        })
        data = response.get_json()

        assert response.status_code == HTTPStatus.CREATED
        assert data["success"] is True
        assert data["data"]["user"]["email"] == "newuser@example.com"

    def test_sign_up_duplicate_email(self, client, session):
        client.post("/auth/sign-up", json={
            "email": "dup@example.com",
            "password": "StrongPass123!",
            "confirmPassword": "StrongPass123!",
            "displayName": "Dup User",
            "acceptTerms": True,
        })
        response = client.post("/auth/sign-up", json={
            "email": "dup@example.com",
            "password": "StrongPass123!",
            "confirmPassword": "StrongPass123!",
            "displayName": "Dup User",
            "acceptTerms": True,
        })
        data = response.get_json()

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert data["success"] is False

    def test_sign_up_password_mismatch(self, client):
        response = client.post("/auth/sign-up", json={
            "email": "mismatch@example.com",
            "password": "StrongPass123!",
            "confirmPassword": "DifferentPass123!",
            "displayName": "Mismatch User",
            "acceptTerms": True,
        })
        data = response.get_json()

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert data["success"] is False

    def test_sign_up_missing_terms(self, client):
        response = client.post("/auth/sign-up", json={
            "email": "noterms@example.com",
            "password": "StrongPass123!",
            "confirmPassword": "StrongPass123!",
            "displayName": "No Terms User",
            "acceptTerms": False,
        })
        data = response.get_json()

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_sign_up_missing_fields(self, client):
        response = client.post("/auth/sign-up", json={
            "email": "nofields@example.com",
        })
        data = response.get_json()

        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_sign_in_success(self, client, auth_headers, session):
        response = client.post("/auth/sign-in", json={
            "email": "testuser@example.com",
            "password": "TestPass123!",
        })
        data = response.get_json()

        assert response.status_code == HTTPStatus.OK
        assert data["success"] is True
        assert "accessToken" in data["data"]["token"]

    def test_sign_in_wrong_password(self, client, auth_headers, session):
        response = client.post("/auth/sign-in", json={
            "email": "testuser@example.com",
            "password": "WrongPassword!",
        })
        data = response.get_json()

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert data["success"] is False

    def test_sign_in_nonexistent_user(self, client):
        response = client.post("/auth/sign-in", json={
            "email": "nobody@example.com",
            "password": "Whatever123!",
        })
        data = response.get_json()

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_refresh_token(self, client, auth_headers, session):
        sign_in_resp = client.post("/auth/sign-in", json={
            "email": "testuser@example.com",
            "password": "TestPass123!",
        })
        refresh_token = sign_in_resp.get_json()["data"]["token"]["refreshToken"]

        response = client.post(
            "/auth/refresh",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        data = response.get_json()

        assert response.status_code == HTTPStatus.OK
        assert "accessToken" in data["data"]

    def test_forgot_password(self, client, auth_headers):
        response = client.post("/auth/forgot-password", json={
            "email": "testuser@example.com",
        })
        data = response.get_json()

        # Should always return 200 for security (even if user doesn't exist)
        assert response.status_code == HTTPStatus.OK
        assert data["success"] is True

    def test_forgot_password_missing_email(self, client):
        response = client.post("/auth/forgot-password", json={})
        data = response.get_json()

        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_auth_health_check(self, client):
        response = client.get("/auth/auth/health")
        data = response.get_json()

        assert response.status_code == HTTPStatus.OK
        assert data["data"]["status"] == "healthy"


class TestProtectedEndpoints:
    def test_access_without_token(self, client):
        response = client.get("/users/")
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_access_with_valid_token(self, client, auth_headers):
        response = client.get("/users/", headers=auth_headers)
        assert response.status_code == HTTPStatus.OK

    def test_access_with_invalid_token(self, client):
        response = client.get(
            "/users/",
            headers={"Authorization": "Bearer invalid_token_here"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
