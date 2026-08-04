from backend.queries import statuses_queries
from backend.tests.integration.db_helpers import DatabaseIntegrationTestCase


class StatusesQueriesIntegrationTestCase(DatabaseIntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.job_id = self.insert_master_job("job")
        self.user_id = self.insert_user(job_id=self.job_id, user_level=1)
        self.status_id = self.insert_master_status(
            "strength",
            status_type="front",
            default_value=10,
        )
        self.user_status_id = self.insert_user_status(
            self.user_id,
            self.status_id,
            status_value=10,
        )

    def test_get_user_statuses_returns_joined_status_rows(self):
        rows = statuses_queries.get_user_statuses(self.user_id)
        rows_by_name = {row["status_name"]: row for row in rows}
        row = rows_by_name[f"{self.prefix}_strength"]

        self.assertEqual(row["status_id"], self.user_status_id)
        self.assertEqual(row["status_value"], 10)
        self.assertEqual(row["status_type"], "front")

    def test_get_user_by_id_returns_user_with_current_job(self):
        user = statuses_queries.get_user_by_id(self.user_id)
        missing_user = statuses_queries.get_user_by_id(-1)

        self.assertEqual(user["id"], self.user_id)
        self.assertEqual(user["user_name"], f"{self.prefix}_user")
        self.assertEqual(user["current_job_id"], self.job_id)
        self.assertEqual(user["current_job_name"], f"{self.prefix}_job")
        self.assertIsNone(missing_user)

    def test_status_cir_applies_category_rules_and_experience(self):
        category_id = self.insert_master_category("study")
        user_category_id = self.insert_user_category(self.user_id, category_id)
        self.insert_status_rule(category_id, self.status_id, gain_per_hours=2.5)

        statuses_queries.status_cir(user_category_id, 3600, self.user_id)

        status_row = self.fetch_one(
            """
            SELECT status_value
            FROM user_statuses
            WHERE user_id=%s
            AND status_id=%s
            """,
            (self.user_id, self.status_id),
        )
        user_row = self.fetch_one(
            """
            SELECT user_level
            FROM users
            WHERE id=%s
            """,
            (self.user_id,),
        )

        self.assertAlmostEqual(status_row["status_value"], 12.5)
        self.assertAlmostEqual(user_row["user_level"], 361)
