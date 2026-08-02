import unittest
from unittest.mock import patch

from flask import Flask
from werkzeug.security import check_password_hash, generate_password_hash

from backend.routes import auth as auth_routes


class AuthRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret-key",
        )
        self.app.register_blueprint(auth_routes.auth_bp)
        self.client = self.app.test_client()

    def test_login_success_sets_session(self):
        password = "correct-password"

        def fake_get_user_by_name(user_name):
            self.assertEqual(user_name, "test_user")
            return {
                "id": 10,
                "password_hash": generate_password_hash(password),
                "is_admin": 1,
            }

        with patch.object(auth_routes, "get_user_by_name", side_effect=fake_get_user_by_name):
            response = self.client.post(
                "/api/login",
                json={
                    "user_name": "test_user",
                    "password": password,
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True})

        with self.client.session_transaction() as session:
            self.assertEqual(session["user_id"], 10)
            self.assertEqual(session["is_admin"], 1)

    def test_login_fails_when_user_does_not_exist(self):
        with patch.object(auth_routes, "get_user_by_name", return_value=None):
            response = self.client.post(
                "/api/login",
                json={
                    "user_name": "missing_user",
                    "password": "password",
                },
            )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "ユーザー名またはパスワードが違います",
        })

    def test_login_fails_with_wrong_password(self):
        user = {
            "id": 10,
            "password_hash": generate_password_hash("correct-password"),
            "is_admin": 0,
        }

        with patch.object(auth_routes, "get_user_by_name", return_value=user):
            response = self.client.post(
                "/api/login",
                json={
                    "user_name": "test_user",
                    "password": "wrong-password",
                },
            )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "ユーザー名またはパスワードが違います",
        })

    def test_register_success_hashes_password(self):
        created_user = {}

        def fake_create_user(user_name, password_hash):
            created_user["user_name"] = user_name
            created_user["password_hash"] = password_hash

        with patch.object(auth_routes, "create_user", side_effect=fake_create_user):
            response = self.client.post(
                "/api/register",
                json={
                    "user_name": "new_user",
                    "password": "plain-password",
                },
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), {
            "success": True,
            "message": "登録完了しました",
        })
        self.assertEqual(created_user["user_name"], "new_user")
        self.assertNotEqual(created_user["password_hash"], "plain-password")
        self.assertTrue(check_password_hash(created_user["password_hash"], "plain-password"))

    def test_register_returns_conflict_when_user_name_is_duplicate(self):
        def fake_create_user(user_name, password_hash):
            raise auth_routes.errors.UniqueViolation("duplicate user_name")

        with patch.object(auth_routes, "create_user", side_effect=fake_create_user):
            response = self.client.post(
                "/api/register",
                json={
                    "user_name": "existing_user",
                    "password": "password",
                },
            )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "そのユーザー名は既に使われています",
        })

    def test_logout_clears_session(self):
        with self.client.session_transaction() as session:
            session["user_id"] = 10
            session["is_admin"] = 1

        response = self.client.post("/api/logout")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True})

        with self.client.session_transaction() as session:
            self.assertNotIn("user_id", session)
            self.assertNotIn("is_admin", session)


if __name__ == "__main__":
    unittest.main()
