from backend.queries.admin import status_queries
from backend.tests.integration.db_helpers import (
    DatabaseIntegrationTestCase,
    make_csv_file,
)


class AdminStatusQueriesIntegrationTestCase(DatabaseIntegrationTestCase):
    def test_add_edit_get_and_lookup_master_status(self):
        status_queries.add_master_status(f"{self.prefix}_status", 10, "front")
        status_id = status_queries.get_status_id(f"{self.prefix}_status")

        status_queries.edit_master_status(
            status_id,
            f"{self.prefix}_status_edited",
            15,
            "back",
            False,
        )

        rows = status_queries.get_master_statuses()
        rows_by_id = {row["id"]: row for row in rows}

        self.assertEqual(rows_by_id[status_id]["status_name"], f"{self.prefix}_status_edited")
        self.assertEqual(rows_by_id[status_id]["default_value"], 15)
        self.assertEqual(rows_by_id[status_id]["status_type"], "back")
        self.assertEqual(rows_by_id[status_id]["is_active"], 0)
        self.assertEqual(
            status_queries.get_status_id_by_name(f"{self.prefix}_status_edited"),
            status_id,
        )
        self.assertIsNone(status_queries.get_status_id(f"{self.prefix}_missing"))

    def test_import_status_csv_inserts_status(self):
        csv_file = make_csv_file(
            "statuses.csv",
            f"status_name,default_value,status_type\n{self.prefix}_imported,12,front\n",
        )

        result = status_queries.import_status_csv(csv_file)
        status_id = status_queries.get_status_id(f"{self.prefix}_imported")
        row = self.fetch_one(
            """
            SELECT default_value, status_type
            FROM master_statuses
            WHERE id=%s
            """,
            (status_id,),
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["imported_count"], 1)
        self.assertEqual(row["default_value"], 12)
        self.assertEqual(row["status_type"], "front")

    def test_import_status_csv_returns_validation_error(self):
        csv_file = make_csv_file(
            "statuses.csv",
            f"status_name,default_value,status_type\n{self.prefix}_bad,10,side\n",
        )

        result = status_queries.import_status_csv(csv_file)

        self.assertFalse(result["success"])
        self.assertEqual(result["imported_count"], 0)
        self.assertEqual(result["errors"][0]["line"], 2)

    def test_delete_master_status_removes_related_rows(self):
        job_id = self.insert_master_job()
        user_id = self.insert_user(job_id=job_id)
        category_id = self.insert_master_category()
        status_id = self.insert_master_status()
        target_job_id = self.insert_master_job("target_job")
        self.insert_user_status(user_id, status_id)
        self.insert_status_rule(category_id, status_id)
        self.insert_job_requirement(target_job_id, status_id)

        result = status_queries.delete_master_status(status_id)

        self.assertTrue(result["deleted"])
        self.assertEqual(result["deleted_status_rules"], 1)
        self.assertEqual(result["deleted_job_requirements"], 1)
        self.assertEqual(result["deleted_user_statuses"], 1)
        self.assertIsNone(self.fetch_one(
            "SELECT id FROM master_statuses WHERE id=%s",
            (status_id,),
        ))

    def test_delete_master_status_returns_false_when_missing(self):
        result = status_queries.delete_master_status(-1)

        self.assertEqual(result, {
            "deleted": False,
            "status_id": -1,
        })
