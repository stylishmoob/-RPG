from backend.queries.admin import achievement_queries
from backend.tests.integration.db_helpers import (
    DatabaseIntegrationTestCase,
    make_csv_file,
)


class AdminAchievementQueriesIntegrationTestCase(DatabaseIntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.category_id = self.insert_master_category("study")

    def test_add_edit_and_get_master_achievement(self):
        achievement_queries.add_master_achievement(
            self.category_id,
            10,
            f"{self.prefix}_achievement",
            f"{self.prefix}_title",
        )
        achievement = self.fetch_one(
            """
            SELECT id
            FROM master_achievements
            WHERE achievement_name=%s
            """,
            (f"{self.prefix}_achievement",),
        )

        achievement_queries.edit_master_achievement(
            achievement["id"],
            self.category_id,
            20,
            f"{self.prefix}_achievement_edited",
            f"{self.prefix}_title_edited",
            False,
        )

        rows = achievement_queries.get_master_achievements()
        rows_by_id = {row["id"]: row for row in rows}
        row = rows_by_id[achievement["id"]]

        self.assertEqual(row["category_id"], self.category_id)
        self.assertEqual(row["category_name"], f"{self.prefix}_study")
        self.assertEqual(row["required_hours"], 20)
        self.assertEqual(row["achievement_name"], f"{self.prefix}_achievement_edited")
        self.assertEqual(row["title_name"], f"{self.prefix}_title_edited")
        self.assertEqual(row["is_active"], 0)

    def test_import_achievement_csv_inserts_achievement(self):
        csv_file = make_csv_file(
            "achievements.csv",
            (
                "category_name,required_hours,achievement_name,title_name\n"
                f"{self.prefix}_study,5,{self.prefix}_imported,{self.prefix}_imported_title\n"
            ),
        )

        result = achievement_queries.import_achievement_csv(csv_file)
        row = self.fetch_one(
            """
            SELECT required_category_id, required_hours, title_name
            FROM master_achievements
            WHERE achievement_name=%s
            """,
            (f"{self.prefix}_imported",),
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["imported_count"], 1)
        self.assertEqual(row["required_category_id"], self.category_id)
        self.assertEqual(row["required_hours"], 5)
        self.assertEqual(row["title_name"], f"{self.prefix}_imported_title")

    def test_import_achievement_csv_returns_validation_error_for_missing_category(self):
        csv_file = make_csv_file(
            "achievements.csv",
            (
                "category_name,required_hours,achievement_name,title_name\n"
                f"{self.prefix}_missing,5,{self.prefix}_bad,{self.prefix}_bad_title\n"
            ),
        )

        result = achievement_queries.import_achievement_csv(csv_file)

        self.assertFalse(result["success"])
        self.assertEqual(result["imported_count"], 0)
        self.assertEqual(result["errors"][0]["line"], 2)

    def test_delete_master_achievement_removes_user_achievements(self):
        job_id = self.insert_master_job()
        user_id = self.insert_user(job_id=job_id)
        achievement_id = self.insert_master_achievement(self.category_id)
        self.insert_user_achievement(user_id, achievement_id)

        result = achievement_queries.delete_master_achievement(achievement_id)

        self.assertTrue(result["deleted"])
        self.assertEqual(result["deleted_user_achievements"], 1)
        self.assertIsNone(self.fetch_one(
            "SELECT id FROM master_achievements WHERE id=%s",
            (achievement_id,),
        ))

    def test_delete_master_achievement_returns_false_when_missing(self):
        result = achievement_queries.delete_master_achievement(-1)

        self.assertEqual(result, {
            "deleted": False,
            "achievement_id": -1,
        })
