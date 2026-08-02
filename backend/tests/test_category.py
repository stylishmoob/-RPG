import unittest
from unittest.mock import patch

from flask import Flask

from backend.routes import category_routes


class CategoryRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret-key",
        )
        self.app.register_blueprint(category_routes.category_bp)
        self.client = self.app.test_client()

    def login(self, user_id=42):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id

    def test_category_requires_login(self):
        response = self.client.get("/api/category")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "login required",
        })

    def test_category_returns_user_and_master_categories(self):
        self.login(user_id=42)

        with (
            patch.object(category_routes, "get_user_categories", return_value=[
                {
                    "category_id": "3",
                    "category_name": "読書",
                },
                {
                    "category_id": "4",
                    "category_name": "運動",
                },
            ]) as get_user_categories,
            patch.object(category_routes, "get_user_master_categories", return_value=[
                {
                    "id": "1",
                    "category_name": "学習",
                },
                {
                    "id": "2",
                    "category_name": "制作",
                },
            ]) as get_user_master_categories,
        ):
            response = self.client.get("/api/category")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "user_categories": [
                {
                    "id": "3",
                    "name": "読書",
                },
                {
                    "id": "4",
                    "name": "運動",
                },
            ],
            "master_categories": [
                {
                    "id": "1",
                    "name": "学習",
                },
                {
                    "id": "2",
                    "name": "制作",
                },
            ],
        })
        get_user_categories.assert_called_once_with(42)
        get_user_master_categories.assert_called_once_with()

    def test_add_category_requires_login(self):
        response = self.client.post(
            "/api/category/add",
            json={
                "master_category_id": "2",
            },
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "login required",
        })

    def test_add_category_calls_query_for_logged_in_user(self):
        self.login(user_id=42)

        with patch.object(category_routes, "add_user_category") as add_user_category:
            response = self.client.post(
                "/api/category/add",
                json={
                    "master_category_id": "2",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True})
        add_user_category.assert_called_once_with(42, "2")

    def test_delete_category_requires_login(self):
        response = self.client.delete("/api/category/3")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "login required",
        })

    def test_delete_category_calls_query_for_logged_in_user(self):
        self.login(user_id=42)

        with patch.object(category_routes, "delete_user_category") as delete_user_category:
            response = self.client.delete("/api/category/3")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True})
        delete_user_category.assert_called_once_with(42, 3)


if __name__ == "__main__":
    unittest.main()
