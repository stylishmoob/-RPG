from backend.queries import achievements_queries
from backend.tests.integration.db_helpers import DatabaseIntegrationTestCase


class AchievementsQueriesIntegrationTestCase(DatabaseIntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.job_id = self.insert_master_job()
        self.user_id = self.insert_user(job_id=self.job_id)
        self.other_user_id = self.insert_user("other_user", job_id=self.job_id)
        self.category_id = self.insert_master_category("study")
        self.user_category_id = self.insert_user_category(self.user_id, self.category_id)

    def test_get_user_achievements_returns_active_achievements_for_user(self):
        active_achievement_id = self.insert_master_achievement(
            self.category_id,
            "active_achievement",
            required_hours=1,
            is_active=1,
        )
        inactive_achievement_id = self.insert_master_achievement(
            self.category_id,
            "inactive_achievement",
            required_hours=1,
            is_active=0,
        )
        other_achievement_id = self.insert_master_achievement(
            self.category_id,
            "other_achievement",
            required_hours=1,
            is_active=1,
        )
        self.insert_user_achievement(self.user_id, active_achievement_id)
        self.insert_user_achievement(self.user_id, inactive_achievement_id)
        self.insert_user_achievement(self.other_user_id, other_achievement_id)

        rows = achievements_queries.get_user_achievements(self.user_id)
        achievement_names = {row["achievement_name"] for row in rows}

        self.assertIn(f"{self.prefix}_active_achievement", achievement_names)
        self.assertNotIn(f"{self.prefix}_inactive_achievement", achievement_names)
        self.assertNotIn(f"{self.prefix}_other_achievement", achievement_names)

    def test_check_category_achievement_grants_only_new_eligible_achievements(self):
        eligible_achievement_id = self.insert_master_achievement(
            self.category_id,
            "eligible_achievement",
            required_hours=1,
            is_active=1,
        )
        ineligible_achievement_id = self.insert_master_achievement(
            self.category_id,
            "ineligible_achievement",
            required_hours=10,
            is_active=1,
        )
        inactive_achievement_id = self.insert_master_achievement(
            self.category_id,
            "inactive_achievement",
            required_hours=1,
            is_active=0,
        )
        self.insert_time_log(
            self.user_id,
            self.user_category_id,
            duration_seconds=7200,
        )

        new_count = achievements_queries.check_category_achievement(self.user_id)
        second_count = achievements_queries.check_category_achievement(self.user_id)

        rows = self.fetch_all(
            """
            SELECT achievement_id
            FROM user_achievements
            WHERE user_id=%s
            """,
            (self.user_id,),
        )
        achievement_ids = {row["achievement_id"] for row in rows}

        self.assertEqual(new_count, 1)
        self.assertEqual(second_count, 0)
        self.assertIn(eligible_achievement_id, achievement_ids)
        self.assertNotIn(ineligible_achievement_id, achievement_ids)
        self.assertNotIn(inactive_achievement_id, achievement_ids)
