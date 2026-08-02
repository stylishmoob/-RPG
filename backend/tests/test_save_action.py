import unittest
from unittest.mock import Mock, patch

from flask import Flask

from backend.services import action_service


class SaveActionRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret-key",
        )
        self.app.register_blueprint(action_service.action_bp)
        self.client = self.app.test_client()

    def login(self, user_id=42):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id

    def test_save_action_requires_login(self):
        response = self.client.post(
            "/api/save_action",
            json={
                "category_id": "7",
                "start_time": "2026-08-02T09:00:00",
                "end_time": "2026-08-02T10:00:00",
                "duration_seconds": "3600",
            },
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "login required",
        })

    def test_save_action_calls_update_steps_for_logged_in_user(self):
        self.login(user_id=42)

        call_order = []

        def make_step(name):
            def step(*args):
                call_order.append((name, args))
            return Mock(side_effect=step)

        save_time_logs = make_step("save_time_logs")
        status_cir = make_step("status_cir")
        check_category_achievement = make_step("check_category_achievement")
        check_user_job = make_step("check_user_job")

        with (
            patch.object(action_service, "save_time_logs", save_time_logs),
            patch.object(action_service, "status_cir", status_cir),
            patch.object(action_service, "check_category_achievement", check_category_achievement),
            patch.object(action_service, "check_user_job", check_user_job),
        ):
            response = self.client.post(
                "/api/save_action",
                json={
                    "category_id": "7",
                    "start_time": "2026-08-02T09:00:00",
                    "end_time": "2026-08-02T10:00:00",
                    "duration_seconds": "3600",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True})

        save_time_logs.assert_called_once_with(
            42,
            "7",
            "2026-08-02T09:00:00",
            "2026-08-02T10:00:00",
            3600,
        )
        status_cir.assert_called_once_with("7", 3600, 42)
        check_category_achievement.assert_called_once_with(42)
        check_user_job.assert_called_once_with(42)
        self.assertEqual(call_order, [
            (
                "save_time_logs",
                (
                    42,
                    "7",
                    "2026-08-02T09:00:00",
                    "2026-08-02T10:00:00",
                    3600,
                ),
            ),
            ("status_cir", ("7", 3600, 42)),
            ("check_category_achievement", (42,)),
            ("check_user_job", (42,)),
        ])


if __name__ == "__main__":
    unittest.main()
