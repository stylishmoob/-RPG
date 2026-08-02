import unittest
from unittest.mock import patch

from flask import Flask

from backend.routes import home_routes


class HomeRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret-key",
        )
        self.app.register_blueprint(home_routes.home_bp)
        self.client = self.app.test_client()

    def login(self, user_id=42, is_admin=0):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id
            session["is_admin"] = is_admin

    def test_home_requires_login(self):
        response = self.client.get("/api/home")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "login required",
        })

    def test_home_returns_user_summary_for_logged_in_user(self):
        self.login(user_id=42, is_admin=1)

        with (
            patch.object(home_routes, "get_time_logs", return_value=[]) as get_time_logs,
            patch.object(home_routes, "get_user_categories", return_value=[
                {
                    "category_id": "7",
                    "category_name": "読書",
                },
            ]) as get_user_categories,
            patch.object(home_routes, "get_today_logs", return_value=[
                {
                    "category_id": "7",
                    "category_name": "読書",
                    "start_time": "09:00:00",
                    "end_time": "10:00:00",
                    "duration_seconds": 3600,
                },
            ]) as get_today_logs,
            patch.object(home_routes, "get_user_statuses", return_value=[
                {
                    "status_id": "1",
                    "status_name": "HP",
                    "status_value": 100,
                    "status_type": "front",
                },
            ]) as get_user_statuses,
            patch.object(home_routes, "get_user_achievements", return_value=[
                {
                    "achievement_name": "読書1時間達成!",
                    "title_name": "読書入門者",
                },
            ]) as get_user_achievements,
            patch.object(home_routes, "get_user_jobs", return_value=[
                {
                    "job_id": "2",
                    "job_name": "放浪者",
                },
            ]) as get_user_jobs,
            patch.object(home_routes, "get_user_by_id", return_value={
                "id": 42,
                "user_name": "hero",
                "current_job_id": "2",
                "current_job_name": "放浪者",
                "user_level": 3.45,
            }) as get_user_by_id,
        ):
            response = self.client.get("/api/home")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "user": {
                "id": 42,
                "name": "hero",
                "current_job_id": "2",
                "current_job_name": "放浪者",
                "level": 3,
            },
            "exp": {
                "current": 45,
                "next": 100,
                "percent": 45.0,
            },
            "job": [
                {
                    "id": "2",
                    "name": "放浪者",
                },
            ],
            "user_statuses": [
                {
                    "id": "1",
                    "name": "HP",
                    "value": 100,
                    "type": "front",
                },
            ],
            "user_achievements": [
                {
                    "achievement_name": "読書1時間達成!",
                    "title_name": "読書入門者",
                },
            ],
            "user_categories": [
                {
                    "id": "7",
                    "name": "読書",
                },
            ],
            "today_logs": [
                {
                    "category_id": "7",
                    "category_name": "読書",
                    "start_time": "09:00:00",
                    "end_time": "10:00:00",
                    "duration_seconds": 3600,
                },
            ],
            "is_admin": True,
        })

        for query_mock in (
            get_time_logs,
            get_user_categories,
            get_today_logs,
            get_user_statuses,
            get_user_achievements,
            get_user_jobs,
            get_user_by_id,
        ):
            query_mock.assert_called_once_with(42)

    def test_home_returns_non_admin_flag_for_normal_user(self):
        self.login(user_id=5, is_admin=0)

        with (
            patch.object(home_routes, "get_time_logs", return_value=[]),
            patch.object(home_routes, "get_user_categories", return_value=[]),
            patch.object(home_routes, "get_today_logs", return_value=[]),
            patch.object(home_routes, "get_user_statuses", return_value=[]),
            patch.object(home_routes, "get_user_achievements", return_value=[]),
            patch.object(home_routes, "get_user_jobs", return_value=[]),
            patch.object(home_routes, "get_user_by_id", return_value={
                "id": 5,
                "user_name": "normal_user",
                "current_job_id": "2",
                "current_job_name": "放浪者",
                "user_level": 1.0,
            }),
        ):
            response = self.client.get("/api/home")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.get_json()["is_admin"])


if __name__ == "__main__":
    unittest.main()
