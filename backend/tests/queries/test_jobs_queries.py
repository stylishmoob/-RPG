from backend.queries import jobs_queries
from backend.tests.integration.db_helpers import DatabaseIntegrationTestCase


class JobsQueriesIntegrationTestCase(DatabaseIntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.current_job_id = self.insert_master_job("current_job")
        self.user_id = self.insert_user(job_id=self.current_job_id)
        self.insert_user_job(self.user_id, self.current_job_id)

    def test_get_user_jobs_returns_only_active_jobs_for_user(self):
        active_job_id = self.insert_master_job("active_job", is_active=1)
        inactive_job_id = self.insert_master_job("inactive_job", is_active=0)
        other_job_id = self.insert_master_job("other_job", is_active=1)
        other_user_id = self.insert_user("other_user", job_id=other_job_id)
        self.insert_user_job(self.user_id, active_job_id)
        self.insert_user_job(self.user_id, inactive_job_id)
        self.insert_user_job(other_user_id, other_job_id)

        rows = jobs_queries.get_user_jobs(self.user_id)
        job_ids = {row["job_id"] for row in rows}

        self.assertIn(self.current_job_id, job_ids)
        self.assertIn(active_job_id, job_ids)
        self.assertNotIn(inactive_job_id, job_ids)
        self.assertNotIn(other_job_id, job_ids)

    def test_update_current_job_updates_owned_active_job(self):
        next_job_id = self.insert_master_job("next_job", is_active=1)
        self.insert_user_job(self.user_id, next_job_id)

        result = jobs_queries.update_current_job(self.user_id, next_job_id)

        row = self.fetch_one(
            """
            SELECT current_job_id
            FROM users
            WHERE id=%s
            """,
            (self.user_id,),
        )
        self.assertEqual(result, {
            "updated": True,
            "current_job_id": next_job_id,
        })
        self.assertEqual(row["current_job_id"], next_job_id)

    def test_update_current_job_rejects_unowned_or_inactive_job(self):
        inactive_job_id = self.insert_master_job("inactive_job", is_active=0)
        self.insert_user_job(self.user_id, inactive_job_id)

        result = jobs_queries.update_current_job(self.user_id, inactive_job_id)

        row = self.fetch_one(
            """
            SELECT current_job_id
            FROM users
            WHERE id=%s
            """,
            (self.user_id,),
        )
        self.assertEqual(result, {
            "updated": False,
            "reason": "job_not_owned",
        })
        self.assertEqual(row["current_job_id"], self.current_job_id)

    def test_check_user_job_unlocks_jobs_when_requirements_are_met(self):
        status_id = self.insert_master_status("strength")
        self.insert_user_status(self.user_id, status_id, status_value=15)

        eligible_job_id = self.insert_master_job("eligible_job")
        ineligible_job_id = self.insert_master_job("ineligible_job")
        self.insert_job_requirement(eligible_job_id, status_id, required_value=10)
        self.insert_job_requirement(ineligible_job_id, status_id, required_value=99)

        new_job_ids = jobs_queries.check_user_job(self.user_id)
        second_job_ids = jobs_queries.check_user_job(self.user_id)

        rows = self.fetch_all(
            """
            SELECT job_id
            FROM user_jobs
            WHERE user_id=%s
            """,
            (self.user_id,),
        )
        owned_job_ids = {row["job_id"] for row in rows}

        self.assertIn(eligible_job_id, new_job_ids)
        self.assertNotIn(ineligible_job_id, new_job_ids)
        self.assertNotIn(eligible_job_id, second_job_ids)
        self.assertIn(eligible_job_id, owned_job_ids)
        self.assertNotIn(ineligible_job_id, owned_job_ids)
