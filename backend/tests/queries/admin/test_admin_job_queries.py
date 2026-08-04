from backend.queries.admin import job_queries
from backend.tests.integration.db_helpers import (
    DatabaseIntegrationTestCase,
    make_csv_file,
)


class AdminJobQueriesIntegrationTestCase(DatabaseIntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.status_id = self.insert_master_status("strength")

    def test_add_admin_job_inserts_job_and_requirements(self):
        requirements = [
            {
                "statusId": self.status_id,
                "requiredValue": 10,
            },
        ]

        job_queries.add_admin_job(f"{self.prefix}_job", requirements)

        job = self.fetch_one(
            """
            SELECT id, job_name
            FROM master_jobs
            WHERE job_name=%s
            """,
            (f"{self.prefix}_job",),
        )
        requirement = self.fetch_one(
            """
            SELECT required_status_id, required_status_value
            FROM job_requirements
            WHERE job_id=%s
            """,
            (job["id"],),
        )
        jobs_by_id = {row["id"]: row for row in job_queries.get_master_jobs()}
        requirements_by_job = {
            row["job_id"]: row for row in job_queries.get_job_requirements()
        }

        self.assertEqual(job["job_name"], f"{self.prefix}_job")
        self.assertEqual(requirement["required_status_id"], self.status_id)
        self.assertEqual(requirement["required_status_value"], 10)
        self.assertEqual(jobs_by_id[job["id"]]["job_name"], f"{self.prefix}_job")
        self.assertEqual(requirements_by_job[job["id"]]["required_status_name"], f"{self.prefix}_strength")

    def test_edit_admin_job_updates_job_and_requirement(self):
        job_id = self.insert_master_job("job")
        requirement_id = self.insert_job_requirement(job_id, self.status_id, required_value=10)
        next_status_id = self.insert_master_status("focus", status_type="back")

        job_queries.edit_admin_job(
            job_id,
            f"{self.prefix}_job_edited",
            False,
            True,
            [
                {
                    "id": requirement_id,
                    "statusId": next_status_id,
                    "requiredValue": 25,
                    "isActive": False,
                },
            ],
        )

        job = self.fetch_one(
            """
            SELECT job_name, is_active, is_default
            FROM master_jobs
            WHERE id=%s
            """,
            (job_id,),
        )
        requirement = self.fetch_one(
            """
            SELECT required_status_id, required_status_value, is_active
            FROM job_requirements
            WHERE id=%s
            """,
            (requirement_id,),
        )

        self.assertEqual(job["job_name"], f"{self.prefix}_job_edited")
        self.assertEqual(job["is_active"], 0)
        self.assertEqual(job["is_default"], 1)
        self.assertEqual(requirement["required_status_id"], next_status_id)
        self.assertEqual(requirement["required_status_value"], 25)
        self.assertEqual(requirement["is_active"], 0)

    def test_delete_job_requirement_removes_requirement(self):
        job_id = self.insert_master_job("job")
        requirement_id = self.insert_job_requirement(job_id, self.status_id)

        result = job_queries.delete_job_requirement(requirement_id)

        self.assertEqual(result, {
            "deleted": True,
            "requirement_id": requirement_id,
        })
        self.assertIsNone(self.fetch_one(
            "SELECT id FROM job_requirements WHERE id=%s",
            (requirement_id,),
        ))

    def test_delete_admin_job_removes_job_data_and_updates_current_users(self):
        job_id = self.insert_master_job("job")
        fallback_job_id = self.insert_master_job("fallback", is_active=1, is_default=1)
        user_id = self.insert_user("job_user", job_id=job_id)
        self.insert_user_job(user_id, job_id)
        self.insert_job_requirement(job_id, self.status_id)

        result = job_queries.delete_admin_job(job_id)
        user = self.fetch_one(
            """
            SELECT current_job_id
            FROM users
            WHERE id=%s
            """,
            (user_id,),
        )

        self.assertTrue(result["deleted"])
        self.assertEqual(result["deleted_job_requirements"], 1)
        self.assertEqual(result["deleted_user_jobs"], 1)
        self.assertEqual(result["updated_current_jobs"], 1)
        self.assertNotEqual(user["current_job_id"], job_id)
        self.assertIsNotNone(self.fetch_one(
            "SELECT id FROM master_jobs WHERE id=%s",
            (fallback_job_id,),
        ))
        self.assertIsNone(self.fetch_one(
            "SELECT id FROM master_jobs WHERE id=%s",
            (job_id,),
        ))

    def test_delete_admin_job_raises_when_no_fallback_for_current_users(self):
        job_id = self.insert_master_job("only_active_job")
        user_id = self.insert_user("job_user", job_id=job_id)
        self.insert_user_job(user_id, job_id)

        with self.assertRaises(ValueError):
            job_queries.delete_admin_job(job_id)

        self.assertIsNotNone(self.fetch_one(
            "SELECT id FROM master_jobs WHERE id=%s",
            (job_id,),
        ))

    def test_import_jobs_csv_inserts_job_and_requirement(self):
        csv_file = make_csv_file(
            "jobs.csv",
            (
                "job_name,required_status_name,required_status_value\n"
                f"{self.prefix}_imported_job,{self.prefix}_strength,12\n"
            ),
        )

        result = job_queries.import_jobs_csv(csv_file)
        job = self.fetch_one(
            """
            SELECT id
            FROM master_jobs
            WHERE job_name=%s
            """,
            (f"{self.prefix}_imported_job",),
        )
        requirement = self.fetch_one(
            """
            SELECT required_status_id, required_status_value
            FROM job_requirements
            WHERE job_id=%s
            """,
            (job["id"],),
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["imported_count"], 1)
        self.assertEqual(requirement["required_status_id"], self.status_id)
        self.assertEqual(requirement["required_status_value"], 12)
