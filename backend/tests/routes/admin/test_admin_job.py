import io
import unittest
from unittest.mock import patch

from flask import Flask

from backend.routes.admin import job_routes as admin_job_routes


class AdminJobRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret-key",
        )
        self.app.register_blueprint(admin_job_routes.admin_job_bp)
        self.client = self.app.test_client()

    def login(self, user_id=42, is_admin=1):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id
            session["is_admin"] = is_admin

    def test_jobs_requires_login(self):
        response = self.client.get("/api/admin/jobs")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "login required",
        })

    def test_jobs_requires_admin(self):
        self.login(is_admin=0)

        response = self.client.get("/api/admin/jobs")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "admin required",
        })

    def test_jobs_returns_jobs_requirements_and_statuses(self):
        self.login()

        with (
            patch.object(
                admin_job_routes,
                "get_master_statuses",
                return_value=[
                    {
                        "id": "1",
                        "status_name": "Strength",
                        "status_type": "physical",
                        "is_active": 1,
                    },
                    {
                        "id": "2",
                        "status_name": "Focus",
                        "status_type": "mental",
                        "is_active": 0,
                    },
                ],
            ) as get_master_statuses,
            patch.object(
                admin_job_routes,
                "get_master_jobs",
                return_value=[
                    {
                        "id": "3",
                        "job_name": "Warrior",
                        "is_active": 1,
                        "is_default": 0,
                    },
                    {
                        "id": "4",
                        "job_name": "Novice",
                        "is_active": 0,
                        "is_default": 1,
                    },
                ],
            ) as get_master_jobs,
            patch.object(
                admin_job_routes,
                "get_job_requirements",
                return_value=[
                    {
                        "id": "5",
                        "job_id": "3",
                        "required_status_id": "1",
                        "required_status_name": "Strength",
                        "required_status_value": 10,
                        "is_active": 1,
                    },
                ],
            ) as get_job_requirements,
        ):
            response = self.client.get("/api/admin/jobs")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "masterJobs": [
                {
                    "id": "3",
                    "jobName": "Warrior",
                    "isActive": True,
                    "isDefault": False,
                },
                {
                    "id": "4",
                    "jobName": "Novice",
                    "isActive": False,
                    "isDefault": True,
                },
            ],
            "jobRequirements": [
                {
                    "id": "5",
                    "jobId": "3",
                    "statusId": "1",
                    "statusName": "Strength",
                    "requiredValue": 10,
                    "isActive": True,
                },
            ],
            "masterStatuses": [
                {
                    "id": "1",
                    "name": "Strength",
                    "type": "physical",
                    "is_active": True,
                },
                {
                    "id": "2",
                    "name": "Focus",
                    "type": "mental",
                    "is_active": False,
                },
            ],
        })
        get_master_statuses.assert_called_once_with()
        get_master_jobs.assert_called_once_with()
        get_job_requirements.assert_called_once_with()

    def test_add_job_calls_query(self):
        self.login()
        requirements = [
            {
                "statusId": "1",
                "requiredValue": "10",
            },
        ]

        with patch.object(admin_job_routes, "add_admin_job") as add_admin_job:
            response = self.client.post(
                "/api/admin/jobs/add",
                json={
                    "jobName": "Warrior",
                    "requirements": requirements,
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True})
        add_admin_job.assert_called_once_with("Warrior", requirements)

    def test_edit_job_calls_query(self):
        self.login()
        requirements = [
            {
                "id": "5",
                "statusId": "1",
                "requiredValue": "12",
            },
        ]

        with patch.object(admin_job_routes, "edit_admin_job") as edit_admin_job:
            response = self.client.post(
                "/api/admin/jobs/edit",
                json={
                    "jobId": "3",
                    "jobName": "Warrior",
                    "isActive": True,
                    "isDefault": False,
                    "requirements": requirements,
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True})
        edit_admin_job.assert_called_once_with(
            "3",
            "Warrior",
            True,
            False,
            requirements,
        )

    def test_delete_job_requires_job_id(self):
        self.login()

        response = self.client.post("/api/admin/jobs/delete", json={})

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["success"])
        self.assertIn("message", response.get_json())

    def test_delete_job_returns_query_result(self):
        self.login()

        with patch.object(
            admin_job_routes,
            "delete_admin_job",
            return_value={
                "deleted": True,
                "job_id": "3",
                "deleted_job_requirements": 2,
                "deleted_user_jobs": 1,
            },
        ) as delete_admin_job:
            response = self.client.post(
                "/api/admin/jobs/delete",
                json={
                    "jobId": "3",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "deleted": True,
            "job_id": "3",
            "deleted_job_requirements": 2,
            "deleted_user_jobs": 1,
        })
        delete_admin_job.assert_called_once_with("3")

    def test_delete_job_returns_bad_request_for_value_error(self):
        self.login()

        with patch.object(
            admin_job_routes,
            "delete_admin_job",
            side_effect=ValueError("default job cannot be deleted"),
        ):
            response = self.client.post(
                "/api/admin/jobs/delete",
                json={
                    "jobId": "3",
                },
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
            "success": False,
            "message": "default job cannot be deleted",
        })

    def test_delete_job_requirement_requires_requirement_id(self):
        self.login()

        response = self.client.post("/api/admin/jobs/requirements/delete", json={})

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["success"])
        self.assertIn("message", response.get_json())

    def test_delete_job_requirement_returns_query_result(self):
        self.login()

        with patch.object(
            admin_job_routes,
            "delete_job_requirement",
            return_value={
                "deleted": True,
                "requirement_id": "5",
            },
        ) as delete_job_requirement:
            response = self.client.post(
                "/api/admin/jobs/requirements/delete",
                json={
                    "requirementId": "5",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "success": True,
            "deleted": True,
            "requirement_id": "5",
        })
        delete_job_requirement.assert_called_once_with("5")

    def test_import_jobs_returns_success_result(self):
        self.login()

        with patch.object(
            admin_job_routes,
            "import_jobs_csv",
            return_value={
                "success": True,
                "message": "imported",
                "imported_count": 1,
                "errors": [],
            },
        ) as import_jobs_csv:
            response = self.client.post(
                "/api/admin/jobs/import",
                data={
                    "file": (
                        io.BytesIO(b"job_name,status_name,required_value\nWarrior,Strength,10\n"),
                        "jobs.csv",
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

        import_jobs_csv.assert_called_once()
        csv_file = import_jobs_csv.call_args.args[0]
        self.assertEqual(csv_file.filename, "jobs.csv")

    def test_import_jobs_returns_bad_request_when_result_is_failure(self):
        self.login()

        with patch.object(
            admin_job_routes,
            "import_jobs_csv",
            return_value={
                "success": False,
                "message": "invalid csv",
            },
        ):
            response = self.client.post(
                "/api/admin/jobs/import",
                data={
                    "file": (
                        io.BytesIO(b"wrong_header\nWarrior\n"),
                        "jobs.csv",
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
