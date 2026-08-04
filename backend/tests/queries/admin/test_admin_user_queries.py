from backend.queries.admin import user_queries
from backend.tests.integration.db_helpers import DatabaseIntegrationTestCase


class AdminUserQueriesIntegrationTestCase(DatabaseIntegrationTestCase):
    def test_get_admin_users_and_edit_admin_user_active(self):
        job_id = self.insert_master_job("job")
        user_id = self.insert_user(
            "admin_user",
            job_id=job_id,
            user_level=5,
            is_active=1,
            is_admin=1,
        )

        result = user_queries.edit_admin_user_active(user_id, False)
        users_by_id = {row["id"]: row for row in user_queries.get_admin_users()}

        self.assertEqual(result, {
            "updated": True,
            "user_id": user_id,
        })
        self.assertEqual(users_by_id[user_id]["user_name"], f"{self.prefix}_admin_user")
        self.assertEqual(users_by_id[user_id]["current_job_name"], f"{self.prefix}_job")
        self.assertEqual(users_by_id[user_id]["is_admin"], 1)
        self.assertEqual(users_by_id[user_id]["is_active"], 0)

    def test_reset_admin_user_data_resets_progress_without_deleting_account(self):
        default_job_id = self.insert_master_job("default_job", is_active=1, is_default=1)
        current_job_id = self.insert_master_job("current_job")
        user_id = self.insert_user("reset_user", job_id=current_job_id, user_level=9)
        category_id = self.insert_master_category("study")
        user_category_id = self.insert_user_category(user_id, category_id)
        status_id = self.insert_master_status("focus", default_value=7, is_active=1)
        self.insert_user_status(user_id, status_id, status_value=99)
        self.insert_user_job(user_id, current_job_id)
        achievement_id = self.insert_master_achievement(category_id)
        self.insert_user_achievement(user_id, achievement_id)
        self.insert_time_log(user_id, user_category_id)

        result = user_queries.reset_admin_user_data(user_id)
        user = self.fetch_one(
            """
            SELECT user_level, current_job_id
            FROM users
            WHERE id=%s
            """,
            (user_id,),
        )
        recreated_status = self.fetch_one(
            """
            SELECT status_value
            FROM user_statuses
            WHERE user_id=%s
            AND status_id=%s
            """,
            (user_id, status_id),
        )
        default_user_job = self.fetch_one(
            """
            SELECT id
            FROM user_jobs
            WHERE user_id=%s
            AND job_id=%s
            """,
            (user_id, user["current_job_id"]),
        )

        self.assertTrue(result["reset"])
        self.assertEqual(result["deleted_time_logs"], 1)
        self.assertEqual(result["deleted_user_categories"], 1)
        self.assertEqual(result["deleted_user_statuses"], 1)
        self.assertEqual(result["deleted_user_jobs"], 1)
        self.assertEqual(result["deleted_user_achievements"], 1)
        self.assertEqual(result["updated_users"], 1)
        self.assertGreaterEqual(result["inserted_user_statuses"], 1)
        self.assertEqual(result["inserted_user_jobs"], 1)
        self.assertEqual(user["user_level"], 1)
        self.assertIsNotNone(recreated_status)
        self.assertEqual(recreated_status["status_value"], 7)
        self.assertIsNotNone(default_user_job)
        self.assertNotEqual(user["current_job_id"], current_job_id)
        self.assertIsNotNone(self.fetch_one(
            "SELECT id FROM master_jobs WHERE id=%s",
            (default_job_id,),
        ))

    def test_reset_admin_user_data_raises_for_missing_user(self):
        with self.assertRaises(ValueError):
            user_queries.reset_admin_user_data(-1)

    def test_delete_admin_user_removes_account_and_related_data(self):
        job_id = self.insert_master_job("job")
        user_id = self.insert_user("delete_user", job_id=job_id)
        category_id = self.insert_master_category("study")
        user_category_id = self.insert_user_category(user_id, category_id)
        status_id = self.insert_master_status("focus")
        self.insert_user_status(user_id, status_id)
        self.insert_user_job(user_id, job_id)
        achievement_id = self.insert_master_achievement(category_id)
        self.insert_user_achievement(user_id, achievement_id)
        self.insert_time_log(user_id, user_category_id)

        result = user_queries.delete_admin_user(user_id)

        self.assertTrue(result["deleted"])
        self.assertEqual(result["deleted_users"], 1)
        self.assertEqual(result["deleted_time_logs"], 1)
        self.assertEqual(result["deleted_user_categories"], 1)
        self.assertEqual(result["deleted_user_statuses"], 1)
        self.assertEqual(result["deleted_user_jobs"], 1)
        self.assertEqual(result["deleted_user_achievements"], 1)
        self.assertIsNone(self.fetch_one(
            "SELECT id FROM users WHERE id=%s",
            (user_id,),
        ))

    def test_delete_admin_user_raises_for_missing_user(self):
        with self.assertRaises(ValueError):
            user_queries.delete_admin_user(-1)
