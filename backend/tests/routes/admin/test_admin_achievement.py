import io
import unittest
from unittest.mock import patch

from flask import Flask

from backend.routes.admin import achievement_routes as admin_achievement_routes


class AdminAchievementRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret-key",
        )
        self.app.register_blueprint(admin_achievement_routes.admin_achievement_bp)
        self.client = self.app.test_client()

    def login(self, user_id=42, is_admin=1):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id
            session["is_admin"] = is_admin

    def test_achievements_requires_login(self):
        response = self.client.get("/api/admin/achievements")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "login required",
        })

    def test_achievements_requires_admin(self):
        self.login(is_admin=0)

        response = self.client.get("/api/admin/achievements")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "admin required",
        })

    def test_achievements_returns_master_achievements_and_categories(self):
        self.login()

        with (
            patch.object(
                admin_achievement_routes,
                "get_master_achievements",
                return_value=[
                    {
                        "id": "1",
                        "category_id": "2",
                        "category_name": "Study",
                        "required_hours": 10,
                        "achievement_name": "Study Beginner",
                        "title_name": "Scholar",
                        "is_active": 1,
                    },
                    {
                        "id": "3",
                        "category_id": "4",
                        "category_name": "Training",
                        "required_hours": 20,
                        "achievement_name": "Training Beginner",
                        "title_name": "Runner",
                        "is_active": 0,
                    },
                ],
            ) as get_master_achievements,
            patch.object(
                admin_achievement_routes,
                "get_master_categories",
                return_value=[
                    {
                        "id": "2",
                        "category_name": "Study",
                        "is_active": 1,
                    },
                    {
                        "id": "4",
                        "category_name": "Training",
                        "is_active": 0,
                    },
                ],
            ) as get_master_categories,
        ):
            response = self.client.get("/api/admin/achievements")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "achievements": [
                {
                    "id": "1",
                    "category_id": "2",
                    "category_name": "Study",
                    "required_hours": 10,
                    "achievement_name": "Study Beginner",
                    "title_name": "Scholar",
                    "is_active": True,
                },
                {
                    "id": "3",
                    "category_id": "4",
                    "category_name": "Training",
                    "required_hours": 20,
                    "achievement_name": "Training Beginner",
                    "title_name": "Runner",
                    "is_active": False,
                },
            ],
            "mastercategories": [
                {
                    "id": "2",
                    "name": "Study",
                    "is_active": True,
                },
                {
                    "id": "4",
                    "name": "Training",
                    "is_active": False,
                },
            ],
        })
        get_master_achievements.assert_called_once_with()
        get_master_categories.assert_called_once_with()

    def test_add_achievement_calls_query(self):
        self.login()

        with patch.object(
            admin_achievement_routes,
            "add_master_achievement",
        ) as add_master_achievement:
            response = self.client.post(
                "/api/admin/achievements/add",
                json={
                    "category_id": "2",
                    "required_hours": "10",
                    "achievement_name": "Study Beginner",
                    "title_name": "Scholar",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True})
        add_master_achievement.assert_called_once_with(
            "2",
            "10",
            "Study Beginner",
            "Scholar",
        )

    def test_edit_achievement_calls_query(self):
        self.login()

        with patch.object(
            admin_achievement_routes,
            "edit_master_achievement",
        ) as edit_master_achievement:
            response = self.client.post(
                "/api/admin/achievements/edit",
                json={
                    "achievement_id": "5",
                    "category_id": "2",
                    "required_hours": "12",
                    "achievement_name": "Study Expert",
                    "title_name": "Sage",
                    "is_active": False,
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True})
        edit_master_achievement.assert_called_once_with(
            "5",
            "2",
            "12",
            "Study Expert",
            "Sage",
            False,
        )

    def test_delete_achievement_returns_query_result(self):
        self.login()

        with patch.object(
            admin_achievement_routes,
            "delete_master_achievement",
            return_value={
                "deleted": True,
                "achievement_id": "5",
                "deleted_user_achievements": 2,
            },
        ) as delete_master_achievement:
            response = self.client.post(
                "/api/admin/achievements/delete",
                json={
                    "achievement_id": "5",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "deleted": True,
            "achievement_id": "5",
            "deleted_user_achievements": 2,
        })
        delete_master_achievement.assert_called_once_with("5")

    def test_import_achievement_returns_success_result(self):
        self.login()

        with patch.object(
            admin_achievement_routes,
            "import_achievement_csv",
            return_value={
                "success": True,
                "message": "imported",
                "imported_count": 1,
                "errors": [],
            },
        ) as import_achievement_csv:
            response = self.client.post(
                "/api/admin/achievements/import",
                data={
                    "file": (
                        io.BytesIO(
                            b"category_name,required_hours,achievement_name,title_name\n"
                            b"Study,10,Study Beginner,Scholar\n"
                        ),
                        "achievements.csv",
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

        import_achievement_csv.assert_called_once()
        csv_file = import_achievement_csv.call_args.args[0]
        self.assertEqual(csv_file.filename, "achievements.csv")

    def test_import_achievement_returns_bad_request_when_result_is_failure(self):
        self.login()

        with patch.object(
            admin_achievement_routes,
            "import_achievement_csv",
            return_value={
                "success": False,
                "message": "invalid csv",
            },
        ):
            response = self.client.post(
                "/api/admin/achievements/import",
                data={
                    "file": (
                        io.BytesIO(b"wrong_header\nStudy\n"),
                        "achievements.csv",
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
