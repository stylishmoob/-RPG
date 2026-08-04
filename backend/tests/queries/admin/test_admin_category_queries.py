from backend.queries.admin import category_queries
from backend.tests.integration.db_helpers import (
    DatabaseIntegrationTestCase,
    make_csv_file,
)


class AdminCategoryQueriesIntegrationTestCase(DatabaseIntegrationTestCase):
    def test_add_edit_get_and_lookup_master_category(self):
        category_queries.add_master_category(f"{self.prefix}_category")
        category_id = category_queries.get_category_id(f"{self.prefix}_category")

        category_queries.edit_master_category(
            category_id,
            f"{self.prefix}_category_edited",
            False,
        )

        rows = category_queries.get_master_categories()
        rows_by_id = {row["id"]: row for row in rows}

        self.assertEqual(rows_by_id[category_id]["category_name"], f"{self.prefix}_category_edited")
        self.assertEqual(rows_by_id[category_id]["is_active"], 0)
        self.assertIsNone(category_queries.get_category_id(f"{self.prefix}_missing"))

    def test_import_category_csv_inserts_categories_and_default_achievements(self):
        csv_file = make_csv_file(
            "categories.csv",
            f"category_name\n{self.prefix}_imported\n",
        )

        result = category_queries.import_category_csv(csv_file)
        category_id = category_queries.get_category_id(f"{self.prefix}_imported")
        achievement_count = self.fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM master_achievements
            WHERE required_category_id=%s
            """,
            (category_id,),
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["imported_count"], 1)
        self.assertIsNotNone(category_id)
        self.assertEqual(achievement_count["count"], 8)

    def test_import_category_csv_returns_validation_error(self):
        csv_file = make_csv_file("categories.csv", "category_name\n\n")

        result = category_queries.import_category_csv(csv_file)

        self.assertFalse(result["success"])
        self.assertEqual(result["imported_count"], 0)
        self.assertEqual(result["errors"][0]["line"], 2)

    def test_delete_master_category_removes_related_rows(self):
        job_id = self.insert_master_job()
        user_id = self.insert_user(job_id=job_id)
        status_id = self.insert_master_status()
        category_id = self.insert_master_category()
        user_category_id = self.insert_user_category(user_id, category_id)
        achievement_id = self.insert_master_achievement(category_id)
        self.insert_user_achievement(user_id, achievement_id)
        self.insert_status_rule(category_id, status_id)
        self.insert_time_log(user_id, user_category_id)

        result = category_queries.delete_master_category(category_id)

        self.assertTrue(result["deleted"])
        self.assertEqual(result["deleted_time_logs"], 1)
        self.assertEqual(result["deleted_user_achievements"], 1)
        self.assertEqual(result["deleted_achievements"], 1)
        self.assertEqual(result["deleted_status_rules"], 1)
        self.assertEqual(result["deleted_user_categories"], 1)
        self.assertIsNone(self.fetch_one(
            "SELECT id FROM master_categories WHERE id=%s",
            (category_id,),
        ))

    def test_delete_master_category_returns_false_when_missing(self):
        result = category_queries.delete_master_category(-1)

        self.assertEqual(result, {
            "deleted": False,
            "category_id": -1,
        })
