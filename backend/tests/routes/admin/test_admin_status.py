import io
import unittest
from unittest.mock import patch

from flask import Flask

from backend.routes.admin import status_routes as admin_status_routes


class AdminStatusRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret-key",
        )
        self.app.register_blueprint(admin_status_routes.admin_status_bp)
        self.client = self.app.test_client()

    def login(self, user_id=42, is_admin=1):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id
            session["is_admin"] = is_admin

    def test_statuses_requires_login(self):
        response = self.client.get("/api/admin/statuses")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "login required",
        })

    def test_statuses_requires_admin(self):
        self.login(is_admin=0)

        response = self.client.get("/api/admin/statuses")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "admin required",
        })

    def test_statuses_returns_master_statuses(self):
        self.login()

        with patch.object(
            admin_status_routes,
            "get_master_statuses",
            return_value=[
                {
                    "id": "1",
                    "status_name": "Strength",
                    "status_type": "physical",
                    "default_value": 10,
                    "is_active": 1,
                },
                {
                    "id": "2",
                    "status_name": "Intelligence",
                    "status_type": "mental",
                    "default_value": 5,
                    "is_active": 0,
                },
            ],
        ) as get_master_statuses:
            response = self.client.get("/api/admin/statuses")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "masterStatuses": [
                {
                    "id": "1",
                    "name": "Strength",
                    "type": "physical",
                    "default_value": 10,
                    "isActive": True,
                },
                {
                    "id": "2",
                    "name": "Intelligence",
                    "type": "mental",
                    "default_value": 5,
                    "isActive": False,
                },
            ],
        })
        get_master_statuses.assert_called_once_with()

    def test_add_status_calls_query(self):
        self.login()

        with patch.object(admin_status_routes, "add_master_status") as add_master_status:
            response = self.client.post(
                "/api/admin/statuses/add",
                json={
                    "status_name": "Strength",
                    "default_value": "10",
                    "status_type": "physical",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True})
        add_master_status.assert_called_once_with("Strength", "10", "physical")

    def test_edit_status_calls_query(self):
        self.login()

        with patch.object(admin_status_routes, "edit_master_status") as edit_master_status:
            response = self.client.post(
                "/api/admin/statuses/edit",
                json={
                    "status_id": "3",
                    "status_name": "Focus",
                    "default_value": "12",
                    "status_type": "mental",
                    "status_is_active": False,
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True})
        edit_master_status.assert_called_once_with("3", "Focus", "12", "mental", False)

    def test_delete_status_returns_query_result(self):
        self.login()

        with patch.object(
            admin_status_routes,
            "delete_master_status",
            return_value={
                "deleted": True,
                "status_id": "3",
                "deleted_user_statuses": 2,
                "deleted_status_rules": 1,
                "deleted_job_requirements": 1,
            },
        ) as delete_master_status:
            response = self.client.post(
                "/api/admin/statuses/delete",
                json={
                    "status_id": "3",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "deleted": True,
            "status_id": "3",
            "deleted_user_statuses": 2,
            "deleted_status_rules": 1,
            "deleted_job_requirements": 1,
        })
        delete_master_status.assert_called_once_with("3")

    def test_import_status_returns_success_result(self):
        self.login()

        with patch.object(
            admin_status_routes,
            "import_status_csv",
            return_value={
                "success": True,
                "message": "imported",
                "imported_count": 1,
                "errors": [],
            },
        ) as import_status_csv:
            response = self.client.post(
                "/api/admin/statuses/import",
                data={
                    "file": (
                        io.BytesIO(b"status_name,default_value,status_type\nHP,10,physical\n"),
                        "statuses.csv",
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

        import_status_csv.assert_called_once()
        csv_file = import_status_csv.call_args.args[0]
        self.assertEqual(csv_file.filename, "statuses.csv")

    def test_import_status_returns_bad_request_when_result_is_failure(self):
        self.login()

        with patch.object(
            admin_status_routes,
            "import_status_csv",
            return_value={
                "success": False,
                "message": "invalid csv",
            },
        ):
            response = self.client.post(
                "/api/admin/statuses/import",
                data={
                    "file": (
                        io.BytesIO(b"wrong_header\nHP\n"),
                        "statuses.csv",
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
