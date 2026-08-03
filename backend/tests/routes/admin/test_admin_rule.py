import io
import unittest
from unittest.mock import patch

from flask import Flask

from backend.routes.admin import rule_routes as admin_rule_routes


class AdminRuleRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret-key",
        )
        self.app.register_blueprint(admin_rule_routes.admin_rule_bp)
        self.client = self.app.test_client()

    def login(self, user_id=42, is_admin=1):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id
            session["is_admin"] = is_admin

    def test_status_rules_requires_login(self):
        response = self.client.get("/api/admin/status_rules")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "login required",
        })

    def test_status_rules_requires_admin(self):
        self.login(is_admin=0)

        response = self.client.get("/api/admin/status_rules")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "admin required",
        })

    def test_status_rules_returns_rules_categories_and_statuses(self):
        self.login()

        with (
            patch.object(
                admin_rule_routes,
                "get_master_status_rules",
                return_value=[
                    {
                        "id": "1",
                        "category_id": "2",
                        "category_name": "Study",
                        "status_id": "3",
                        "status_name": "Focus",
                        "gain_per_hours": 1.5,
                        "is_active": 1,
                    },
                ],
            ) as get_master_status_rules,
            patch.object(
                admin_rule_routes,
                "get_master_categories",
                return_value=[
                    {
                        "id": "2",
                        "category_name": "Study",
                        "is_active": 1,
                    },
                ],
            ) as get_master_categories,
            patch.object(
                admin_rule_routes,
                "get_master_statuses",
                return_value=[
                    {
                        "id": "3",
                        "status_name": "Focus",
                        "status_type": "mental",
                        "is_active": 0,
                    },
                ],
            ) as get_master_statuses,
        ):
            response = self.client.get("/api/admin/status_rules")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "statusRules": [
                {
                    "id": "1",
                    "category_id": "2",
                    "category_name": "Study",
                    "status_id": "3",
                    "status_name": "Focus",
                    "gain_per_hours": 1.5,
                    "is_active": True,
                },
            ],
            "masterCategories": [
                {
                    "id": "2",
                    "name": "Study",
                    "is_active": True,
                },
            ],
            "masterStatuses": [
                {
                    "id": "3",
                    "name": "Focus",
                    "type": "mental",
                    "is_active": False,
                },
            ],
        })
        get_master_status_rules.assert_called_once_with()
        get_master_categories.assert_called_once_with()
        get_master_statuses.assert_called_once_with()

    def test_add_status_rule_calls_query(self):
        self.login()

        with patch.object(admin_rule_routes, "add_status_rules") as add_status_rules:
            response = self.client.post(
                "/api/admin/status_rules/add",
                json={
                    "category_id": "2",
                    "status_id": "3",
                    "gain_per_hours": "1.5",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True})
        add_status_rules.assert_called_once_with("2", "3", "1.5")

    def test_edit_status_rule_calls_query(self):
        self.login()

        with patch.object(admin_rule_routes, "edit_status_rules") as edit_status_rules:
            response = self.client.post(
                "/api/admin/status_rules/edit",
                json={
                    "id": "1",
                    "category_id": "2",
                    "status_id": "3",
                    "gain_per_hours": "2",
                    "status_rules_is_active": False,
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True})
        edit_status_rules.assert_called_once_with("1", "2", "3", "2", False)

    def test_delete_status_rule_calls_query(self):
        self.login()

        with patch.object(admin_rule_routes, "delete_status_rule") as delete_status_rule:
            response = self.client.post(
                "/api/admin/status_rules/delete",
                json={
                    "id": "1",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True})
        delete_status_rule.assert_called_once_with("1")

    def test_import_status_rules_returns_success_result(self):
        self.login()

        with patch.object(
            admin_rule_routes,
            "import_status_rules_csv",
            return_value={
                "success": True,
                "message": "imported",
                "imported_count": 1,
                "errors": [],
            },
        ) as import_status_rules_csv:
            response = self.client.post(
                "/api/admin/status_rules/import",
                data={
                    "file": (
                        io.BytesIO(b"category_name,status_name,gain_per_hours\nStudy,Focus,1.5\n"),
                        "status_rules.csv",
                    ),
                },
                content_type="multipart/form-data",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "message": "imported",
            "imported_count": 1,
            "errors": [],
        })

        import_status_rules_csv.assert_called_once()
        csv_file = import_status_rules_csv.call_args.args[0]
        self.assertEqual(csv_file.filename, "status_rules.csv")

    def test_import_status_rules_returns_bad_request_when_result_is_failure(self):
        self.login()

        with patch.object(
            admin_rule_routes,
            "import_status_rules_csv",
            return_value={
                "success": False,
                "message": "invalid csv",
            },
        ):
            response = self.client.post(
                "/api/admin/status_rules/import",
                data={
                    "file": (
                        io.BytesIO(b"wrong_header\nStudy\n"),
                        "status_rules.csv",
                    ),
                },
                content_type="multipart/form-data",
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "invalid csv",
        })


if __name__ == "__main__":
    unittest.main()
