"""Tests for /auth/* routes."""
from unittest.mock import MagicMock, patch

import pytest

from tests.conftest import FAKE_PROJECT, FAKE_USER


class TestLoginPage:
    def test_get_login_shows_form(self, anon_client):
        resp = anon_client.get("/auth/login")
        assert resp.status_code == 200
        assert b"login" in resp.content.lower()

    def test_get_login_redirects_when_authenticated(self, authed_anon_client):
        resp = authed_anon_client.get("/auth/login")
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects"


class TestLoginPost:
    def test_successful_login_sets_cookie_and_redirects(self, anon_client):
        fake_session = MagicMock()
        fake_session.id = "tok123"
        with (
            patch("app.routers.auth.auth_service.authenticate_user", return_value=FAKE_USER),
            patch("app.routers.auth.auth_service.create_session", return_value=fake_session),
        ):
            resp = anon_client.post(
                "/auth/login",
                data={"email": "test@example.com", "password": "secret123"},
            )
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects"
        assert "sf_session" in resp.cookies

    def test_bad_credentials_returns_401(self, anon_client):
        with patch("app.routers.auth.auth_service.authenticate_user", return_value=None):
            resp = anon_client.post(
                "/auth/login",
                data={"email": "x@x.com", "password": "wrong"},
            )
        assert resp.status_code == 401
        assert b"Invalid" in resp.content


class TestSignupPage:
    def test_get_signup_shows_form(self, anon_client):
        resp = anon_client.get("/auth/signup")
        assert resp.status_code == 200

    def test_get_signup_redirects_when_authenticated(self, authed_anon_client):
        resp = authed_anon_client.get("/auth/signup")
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects"


class TestSignupPost:
    def test_successful_signup_redirects(self, anon_client):
        fake_session = MagicMock()
        fake_session.id = "newsession"
        with (
            patch("app.routers.auth.auth_service.create_user", return_value=FAKE_USER),
            patch("app.routers.auth.auth_service.create_session", return_value=fake_session),
        ):
            resp = anon_client.post(
                "/auth/signup",
                data={
                    "email": "new@example.com",
                    "password": "password123",
                    "terms_accepted": "on",
                },
            )
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects"

    def test_signup_without_terms_returns_400(self, anon_client):
        resp = anon_client.post(
            "/auth/signup",
            data={"email": "new@example.com", "password": "password123"},
        )
        assert resp.status_code == 400
        assert b"terms" in resp.content.lower()

    def test_signup_short_password_returns_400(self, anon_client):
        resp = anon_client.post(
            "/auth/signup",
            data={
                "email": "new@example.com",
                "password": "short",
                "terms_accepted": "on",
            },
        )
        assert resp.status_code == 400
        assert b"8 characters" in resp.content

    def test_signup_duplicate_email_returns_400(self, anon_client):
        with patch(
            "app.routers.auth.auth_service.create_user",
            side_effect=ValueError("Email already registered"),
        ):
            resp = anon_client.post(
                "/auth/signup",
                data={
                    "email": "dup@example.com",
                    "password": "password123",
                    "terms_accepted": "on",
                },
            )
        assert resp.status_code == 400
        assert b"already" in resp.content.lower()


class TestLogout:
    def test_logout_deletes_session_and_redirects(self, anon_client):
        with patch("app.routers.auth.auth_service.delete_session") as mock_del:
            resp = anon_client.post(
                "/auth/logout",
                cookies={"sf_session": "tok123"},
            )
        assert resp.status_code == 303
        assert resp.headers["location"] == "/auth/login"
        mock_del.assert_called_once()
        assert mock_del.call_args[0][1] == "tok123"

    def test_logout_without_cookie_still_redirects(self, anon_client):
        resp = anon_client.post("/auth/logout")
        assert resp.status_code == 303
        assert resp.headers["location"] == "/auth/login"


class TestDeleteAccount:
    def test_get_delete_account_page(self, authed_anon_client):
        resp = authed_anon_client.get("/auth/delete-account")
        assert resp.status_code == 200

    def test_get_delete_account_unauthenticated_redirects(self, anon_client):
        resp = anon_client.get("/auth/delete-account")
        assert resp.status_code == 303
        assert "/login" in resp.headers["location"]

    def test_post_delete_account_wrong_email(self, anon_client):
        session_obj = MagicMock()
        session_obj.user_id = "u1"
        with (
            patch("app.routers.auth.auth_service.get_session", return_value=session_obj),
            patch("app.routers.auth.auth_service.get_user_by_id", return_value=FAKE_USER),
        ):
            resp = anon_client.post(
                "/auth/delete-account",
                data={"email_confirm": "wrong@example.com"},
                cookies={"sf_session": "tok"},
            )
        assert resp.status_code == 400
        assert b"does not match" in resp.content


class TestTermsPage:
    def test_terms_page_accessible(self, anon_client):
        resp = anon_client.get("/terms")
        assert resp.status_code == 200
