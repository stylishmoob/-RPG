import unittest
from unittest.mock import patch

from flask import Flask

from backend.routes.admin import user_routes as admin_user_routes


class AdminUserRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret-key",
        )
        self.app.register_blueprint(admin_user_routes.admin_user_bp)
        self.app.register_blueprint(admin_user_routes.reset_user_data_bp)
        self.client = self.app.test_client()

    def login(self, user_id=42, is_admin=1):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id
            session["is_admin"] = is_admin

    def test_users_requires_login(self):
        response = self.client.get("/api/admin/users")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "login required",
        })

    def test_users_requires_admin(self):
        self.login(is_admin=0)

        response = self.client.get("/api/admin/users")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "admin required",
        })

    def test_users_returns_admin_users(self):
        self.login()

        with patch.object(
            admin_user_routes,
            "get_admin_users",
            return_value=[
                {
                    "id": 1,
                    "user_name": "admin",
                    "user_level": 10.5,
                    "current_job_name": "Warrior",
                    "is_admin": 1,
                    "is_active": 1,
                },
                {
                    "id": 2,
                    "user_name": "player",
                    "user_level": 3,
                    "current_job_name": None,
                    "is_admin": 0,
                    "is_active": 0,
                },
            ],
        ) as get_admin_users:
            response = self.client.get("/api/admin/users")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "users": [
                {
                    "id": "1",
                    "username": "admin",
                    "userLevel": "10.5",
                    "userCurrentJob": "Warrior",
                    "isAdmin": True,
                    "isActive": True,
                },
                {
                    "id": "2",
                    "username": "player",
                    "userLevel": "3",
                    "userCurrentJob": None,
                    "isAdmin": False,
                    "isActive": False,
                },
            ],
        })
        get_admin_users.assert_called_once_with()

    def test_edit_user_active_returns_query_result(self):
        self.login()

        with patch.object(
            admin_user_routes,
            "edit_admin_user_active",
            return_value={
                "updated": True,
                "user_id": "2",
            },
        ) as edit_admin_user_active:
            response = self.client.post(
                "/api/admin/users/edit",
                json={
                    "user_id": "2",
                    "is_active": False,
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "updated": True,
            "user_id": "2",
        })
        edit_admin_user_active.assert_called_once_with("2", False)

    def test_delete_user_requires_user_id(self):
        self.login()

        response = self.client.post("/api/admin/users/delete", json={})

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["success"])
        self.assertIn("message", response.get_json())

    def test_delete_user_returns_query_result(self):
        self.login()

        with patch.object(
            admin_user_routes,
            "delete_admin_user",
            return_value={
                "deleted": True,
                "user_id": "2",
                "deleted_time_logs": 4,
                "deleted_user_statuses": 3,
                "deleted_user_jobs": 1,
                "deleted_user_achievements": 2,
            },
        ) as delete_admin_user:
            response = self.client.post(
                "/api/admin/users/delete",
                json={
                    "user_id": "2",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "deleted": True,
            "user_id": "2",
            "deleted_time_logs": 4,
            "deleted_user_statuses": 3,
            "deleted_user_jobs": 1,
            "deleted_user_achievements": 2,
        })
        delete_admin_user.assert_called_once_with("2")

    def test_delete_user_returns_bad_request_for_value_error(self):
        self.login()

        with patch.object(
            admin_user_routes,
            "delete_admin_user",
            side_effect=ValueError("user not found"),
        ):
            response = self.client.post(
                "/api/admin/users/delete",
                json={
                    "user_id": "999",
                },
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "user not found",
        })

    def test_reset_user_data_requires_user_id(self):
        self.login()

        response = self.client.post("/api/reset_user_data", json={})

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["success"])
        self.assertIn("message", response.get_json())

    def test_reset_user_data_returns_query_result(self):
        self.login()

        with patch.object(
            admin_user_routes,
            "reset_admin_user_data",
            return_value={
                "reset": True,
                "user_id": "2",
                "current_job_id": "1",
            },
        ) as reset_admin_user_data:
            response = self.client.post(
                "/api/reset_user_data",
                json={
                    "user_id": "2",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "reset": True,
            "user_id": "2",
            "current_job_id": "1",
        })
        reset_admin_user_data.assert_called_once_with("2")

    def test_reset_user_data_returns_bad_request_for_value_error(self):
        self.login()

        with patch.object(
            admin_user_routes,
            "reset_admin_user_data",
            side_effect=ValueError("default job not found"),
        ):
            response = self.client.post(
                "/api/reset_user_data",
                json={
                    "user_id": "2",
                },
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "default job not found",
        })


if __name__ == "__main__":
    unittest.main()
