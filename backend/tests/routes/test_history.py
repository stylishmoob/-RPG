import unittest
from unittest.mock import patch

from flask import Flask

from backend.routes import history_routes


class HistoryRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret-key",
        )
        self.app.register_blueprint(history_routes.history_bp)
        self.client = self.app.test_client()

    def login(self, user_id=42):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id

    def test_history_requires_login(self):
        response = self.client.get("/api/history")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "login required",
        })

    def test_history_uses_default_periods_and_returns_summaries(self):
        self.login(user_id=42)

        with (
            patch.object(history_routes, "get_category_summary", return_value=[
                {
                    "category_id": "1",
                    "category_name": "読書",
                    "category_total_seconds": 7200,
                },
            ]) as get_category_summary,
            patch.object(history_routes, "get_daily_summary", return_value=[
                {
                    "category_id": "1",
                    "category_name": "読書",
                    "log_date": "2026-08-03",
                    "daily_total_seconds": 3600,
                },
            ]) as get_daily_summary,
        ):
            response = self.client.get("/api/history")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "categorySummary": [
                {
                    "category_id": "1",
                    "category_name": "読書",
                    "category_total_seconds": 7200,
                },
            ],
            "dailyCategorySummary": [
                {
                    "category_id": "1",
                    "category_name": "読書",
                    "log_date": "2026-08-03",
                    "daily_total_seconds": 3600,
                },
            ],
        })
        get_category_summary.assert_called_once_with("all", 42)
        get_daily_summary.assert_called_once_with("all", 42)

    def test_history_passes_requested_periods_to_queries(self):
        self.login(user_id=7)

        with (
            patch.object(history_routes, "get_category_summary", return_value=[]) as get_category_summary,
            patch.object(history_routes, "get_daily_summary", return_value=[]) as get_daily_summary,
        ):
            response = self.client.get("/api/history?ctx1Period=month&ctx2Period=7days")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "categorySummary": [],
            "dailyCategorySummary": [],
        })
        get_category_summary.assert_called_once_with("month", 7)
        get_daily_summary.assert_called_once_with("7days", 7)

    def test_history_returns_empty_lists_when_no_logs_exist(self):
        self.login(user_id=42)

        with (
            patch.object(history_routes, "get_category_summary", return_value=[]),
            patch.object(history_routes, "get_daily_summary", return_value=[]),
        ):
            response = self.client.get("/api/history")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "categorySummary": [],
            "dailyCategorySummary": [],
        })


if __name__ == "__main__":
    unittest.main()
