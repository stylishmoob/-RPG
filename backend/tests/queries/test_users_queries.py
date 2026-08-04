from backend.queries import users_queries
from backend.tests.integration.db_helpers import DatabaseIntegrationTestCase


class UsersQueriesIntegrationTestCase(DatabaseIntegrationTestCase):
    def test_get_user_by_id_and_name_return_user_with_current_job(self):
        job_id = self.insert_master_job("job")
        user_id = self.insert_user("lookup_user", job_id=job_id, user_level=3.5)

        user_by_id = users_queries.get_user_by_id(user_id)
        user_by_name = users_queries.get_user_by_name(f"{self.prefix}_lookup_user")
        missing_user = users_queries.get_user_by_name(f"{self.prefix}_missing")

        self.assertEqual(user_by_id["id"], user_id)
        self.assertEqual(user_by_id["user_name"], f"{self.prefix}_lookup_user")
        self.assertEqual(user_by_id["current_job_name"], f"{self.prefix}_job")
        self.assertEqual(user_by_name["id"], user_id)
        self.assertEqual(user_by_name["current_job_name"], f"{self.prefix}_job")
        self.assertIsNone(missing_user)

    def test_create_user_creates_default_statuses_and_default_job(self):
        self.insert_master_job("default_job", is_active=1, is_default=1)
        active_status_id = self.insert_master_status(
            "active_status",
            default_value=12,
            is_active=1,
        )
        inactive_status_id = self.insert_master_status(
            "inactive_status",
            default_value=99,
            is_active=0,
        )

        users_queries.create_user(f"{self.prefix}_created_user", "hashed-password")

        user = self.fetch_one(
            """
            SELECT id, password_hash, current_job_id
            FROM users
            WHERE user_name=%s
            """,
            (f"{self.prefix}_created_user",),
        )
        active_status = self.fetch_one(
            """
            SELECT status_value
            FROM user_statuses
            WHERE user_id=%s
            AND status_id=%s
            """,
            (user["id"], active_status_id),
        )
        inactive_status = self.fetch_one(
            """
            SELECT id
            FROM user_statuses
            WHERE user_id=%s
            AND status_id=%s
            """,
            (user["id"], inactive_status_id),
        )
        default_job = self.fetch_one(
            """
            SELECT is_active, is_default
            FROM master_jobs
            WHERE id=%s
            """,
            (user["current_job_id"],),
        )
        user_job_count = self.fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM user_jobs
            WHERE user_id=%s
            AND job_id=%s
            """,
            (user["id"], user["current_job_id"]),
        )

        self.assertEqual(user["password_hash"], "hashed-password")
        self.assertEqual(active_status["status_value"], 12)
        self.assertIsNone(inactive_status)
        self.assertEqual(default_job["is_active"], 1)
        self.assertEqual(default_job["is_default"], 1)
        self.assertEqual(user_job_count["count"], 1)
