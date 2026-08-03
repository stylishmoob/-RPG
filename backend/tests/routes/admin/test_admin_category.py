import io
import unittest
from unittest.mock import patch

from flask import Flask

from backend.routes.admin import category_routes as admin_category_routes


class AdminCategoryRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret-key",
        )
        self.app.register_blueprint(admin_category_routes.admin_category_bp)
        self.client = self.app.test_client()

    def login(self, user_id=42, is_admin=1):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id
            session["is_admin"] = is_admin

    def test_categories_requires_login(self):
        response = self.client.get("/api/admin/categories")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "login required",
        })

    def test_categories_requires_admin(self):
        self.login(is_admin=0)

        response = self.client.get("/api/admin/categories")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "admin required",
        })

    def test_categories_returns_master_categories(self):
        self.login()

        with patch.object(
            admin_category_routes,
            "get_master_categories",
            return_value=[
                {
                    "id": "1",
                    "category_name": "Study",
                    "is_active": 1,
                },
                {
                    "id": "2",
                    "category_name": "Training",
                    "is_active": 0,
                },
            ],
        ) as get_master_categories:
            response = self.client.get("/api/admin/categories")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "MasterCategories": [
                {
                    "id": "1",
                    "name": "Study",
                    "is_active": True,
                },
                {
                    "id": "2",
                    "name": "Training",
                    "is_active": False,
                },
            ],
        })
        get_master_categories.assert_called_once_with()

    def test_add_category_calls_query(self):
        self.login()

        with patch.object(admin_category_routes, "add_master_category") as add_master_category:
            response = self.client.post(
                "/api/admin/categories/add",
                json={
                    "category_name": "Study",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True})
        add_master_category.assert_called_once_with("Study")

    def test_edit_category_calls_query(self):
        self.login()

        with patch.object(admin_category_routes, "edit_master_category") as edit_master_category:
            response = self.client.post(
                "/api/admin/categories/edit",
                json={
                    "category_id": "3",
                    "category_name": "Reading",
                    "is_active": False,
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True})
        edit_master_category.assert_called_once_with("3", "Reading", False)

    def test_delete_category_returns_query_result(self):
        self.login()

        with patch.object(
            admin_category_routes,
            "delete_master_category",
            return_value={
                "deleted": True,
                "category_id": "3",
                "deleted_time_logs": 2,
                "deleted_user_achievements": 1,
                "deleted_achievements": 1,
                "deleted_status_rules": 1,
                "deleted_user_categories": 1,
            },
        ) as delete_master_category:
            response = self.client.post(
                "/api/admin/categories/delete",
                json={
                    "category_id": "3",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "deleted": True,
            "category_id": "3",
            "deleted_time_logs": 2,
            "deleted_user_achievements": 1,
            "deleted_achievements": 1,
            "deleted_status_rules": 1,
            "deleted_user_categories": 1,
        })
        delete_master_category.assert_called_once_with("3")

    def test_import_category_returns_success_result(self):
        self.login()

        with patch.object(
            admin_category_routes,
            "import_category_csv",
            return_value={
                "success": True,
                "message": "imported",
                "imported_count": 1,
                "errors": [],
            },
        ) as import_category_csv:
            response = self.client.post(
                "/api/admin/categories/import",
                data={
                    "file": (
                        io.BytesIO(b"category_name\nStudy\n"),
                        "categories.csv",
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

        import_category_csv.assert_called_once()
        csv_file = import_category_csv.call_args.args[0]
        self.assertEqual(csv_file.filename, "categories.csv")

    def test_import_category_returns_bad_request_when_result_is_failure(self):
        self.login()

        with patch.object(
            admin_category_routes,
            "import_category_csv",
            return_value={
                "success": False,
                "message": "invalid csv",
            },
        ):
            response = self.client.post(
                "/api/admin/categories/import",
                data={
                    "file": (
                        io.BytesIO(b"wrong_header\nStudy\n"),
                        "categories.csv",
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
