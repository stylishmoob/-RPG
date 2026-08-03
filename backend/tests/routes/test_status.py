import unittest
from unittest.mock import patch

from flask import Flask

from backend.routes import status_routes


class StatusRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret-key",
        )
        self.app.register_blueprint(status_routes.status_bp)
        self.client = self.app.test_client()

    def login(self, user_id=42, is_admin=0):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id
            session["is_admin"] = is_admin

    def test_status_requires_login(self):
        response = self.client.get("/api/status")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "login required",
        })

    def test_status_returns_user_status_jobs_and_achievements(self):
        self.login(user_id=42, is_admin=1)

        with (
            patch.object(status_routes, "get_time_logs", return_value=[]) as get_time_logs,
            patch.object(status_routes, "get_user_statuses", return_value=[
                {
                    "status_id": "1",
                    "status_name": "HP",
                    "status_value": 100,
                    "status_type": "front",
                },
                {
                    "status_id": "2",
                    "status_name": "INT",
                    "status_value": 15,
                    "status_type": "back",
                },
            ]) as get_user_statuses,
            patch.object(status_routes, "get_user_achievements", return_value=[
                {
                    "achievement_name": "読書1時間達成!",
                    "title_name": "読書入門者",
                },
            ]) as get_user_achievements,
            patch.object(status_routes, "get_user_jobs", return_value=[
                {
                    "job_id": "2",
                    "job_name": "放浪者",
                },
            ]) as get_user_jobs,
            patch.object(status_routes, "get_user_by_id", return_value={
                "id": 42,
                "user_name": "hero",
                "current_job_id": "2",
                "current_job_name": "放浪者",
                "user_level": 4.25,
            }) as get_user_by_id,
        ):
            response = self.client.get("/api/status")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "user": {
                "id": 42,
                "name": "hero",
                "current_job_id": "2",
                "current_job_name": "放浪者",
                "job": "放浪者",
                "level": 4,
            },
            "exp": {
                "current": 25,
                "next": 100,
                "percent": 25.0,
            },
            "job": [
                {
                    "id": "2",
                    "name": "放浪者",
                },
            ],
            "status": [
                {
                    "id": "1",
                    "name": "HP",
                    "value": 100,
                    "type": "front",
                },
                {
                    "id": "2",
                    "name": "INT",
                    "value": 15,
                    "type": "back",
                },
            ],
            "achievements": [
                {
                    "achievement_name": "読書1時間達成!",
                    "title_name": "読書入門者",
                },
            ],
            "is_admin": True,
        })

        for query_mock in (
            get_time_logs,
            get_user_statuses,
            get_user_achievements,
            get_user_jobs,
            get_user_by_id,
        ):
            query_mock.assert_called_once_with(42)

    def test_status_returns_non_admin_flag_for_normal_user(self):
        self.login(user_id=5, is_admin=0)

        with (
            patch.object(status_routes, "get_time_logs", return_value=[]),
            patch.object(status_routes, "get_user_statuses", return_value=[]),
            patch.object(status_routes, "get_user_achievements", return_value=[]),
            patch.object(status_routes, "get_user_jobs", return_value=[]),
            patch.object(status_routes, "get_user_by_id", return_value={
                "id": 5,
                "user_name": "normal_user",
                "current_job_id": "2",
                "current_job_name": "放浪者",
                "user_level": 1.0,
            }),
        ):
            response = self.client.get("/api/status")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.get_json()["is_admin"])

    def test_update_current_job_requires_login(self):
        response = self.client.post(
            "/api/status/current_job",
            json={
                "currentJobId": "3",
            },
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "login required",
        })

    def test_update_current_job_requires_job_id(self):
        self.login(user_id=42)

        response = self.client.post("/api/status/current_job", json={})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "currentJobIdがありません",
        })

    def test_update_current_job_accepts_current_job_id_alias(self):
        self.login(user_id=42)

        with patch.object(
            status_routes,
            "update_current_job",
            return_value={
                "updated": True,
                "current_job_id": "3",
            },
        ) as update_current_job:
            response = self.client.post(
                "/api/status/current_job",
                json={
                    "current_job_id": "3",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "updated": True,
            "current_job_id": "3",
        })
        update_current_job.assert_called_once_with(42, "3")

    def test_update_current_job_returns_bad_request_when_job_is_not_owned(self):
        self.login(user_id=42)

        with patch.object(
            status_routes,
            "update_current_job",
            return_value={
                "updated": False,
                "reason": "job_not_owned",
            },
        ) as update_current_job:
            response = self.client.post(
                "/api/status/current_job",
                json={
                    "currentJobId": "999",
                },
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "所持していない職業です",
            "updated": False,
            "reason": "job_not_owned",
        })
        update_current_job.assert_called_once_with(42, "999")


if __name__ == "__main__":
    unittest.main()
