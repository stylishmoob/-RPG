from backend.queries.admin import rule_queries
from backend.tests.integration.db_helpers import (
    DatabaseIntegrationTestCase,
    make_csv_file,
)


class AdminRuleQueriesIntegrationTestCase(DatabaseIntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.category_id = self.insert_master_category("study")
        self.status_id = self.insert_master_status("focus")

    def test_add_get_edit_and_delete_status_rule(self):
        rule_queries.add_status_rules(self.category_id, self.status_id, 1.5)
        rule = self.fetch_one(
            """
            SELECT id
            FROM status_up_rules
            WHERE category_id=%s
            AND status_id=%s
            """,
            (self.category_id, self.status_id),
        )
        next_status_id = self.insert_master_status("strength")

        rule_queries.edit_status_rules(
            rule["id"],
            self.category_id,
            next_status_id,
            2.5,
            False,
        )

        rows = rule_queries.get_master_status_rules()
        rows_by_id = {row["id"]: row for row in rows}
        edited_rule = rows_by_id[rule["id"]]

        self.assertEqual(edited_rule["category_name"], f"{self.prefix}_study")
        self.assertEqual(edited_rule["status_id"], next_status_id)
        self.assertEqual(edited_rule["status_name"], f"{self.prefix}_strength")
        self.assertEqual(edited_rule["gain_per_hours"], 2.5)
        self.assertEqual(edited_rule["is_active"], 0)

        rule_queries.delete_status_rule(rule["id"])
        self.assertIsNone(self.fetch_one(
            "SELECT id FROM status_up_rules WHERE id=%s",
            (rule["id"],),
        ))

    def test_delete_status_rules_removes_rule_by_category_and_status(self):
        rule_id = self.insert_status_rule(self.category_id, self.status_id)

        rule_queries.delete_status_rules(self.category_id, self.status_id)

        self.assertIsNone(self.fetch_one(
            "SELECT id FROM status_up_rules WHERE id=%s",
            (rule_id,),
        ))

    def test_import_status_rules_csv_inserts_rule(self):
        csv_file = make_csv_file(
            "status_rules.csv",
            (
                "category_name,status_name,gain_per_hours\n"
                f"{self.prefix}_study,{self.prefix}_focus,3.5\n"
            ),
        )

        result = rule_queries.import_status_rules_csv(csv_file)
        rule = self.fetch_one(
            """
            SELECT gain_per_hours
            FROM status_up_rules
            WHERE category_id=%s
            AND status_id=%s
            """,
            (self.category_id, self.status_id),
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["imported_count"], 1)
        self.assertEqual(rule["gain_per_hours"], 3.5)

    def test_import_status_rules_csv_returns_validation_error(self):
        csv_file = make_csv_file(
            "status_rules.csv",
            (
                "category_name,status_name,gain_per_hours\n"
                f"{self.prefix}_missing,{self.prefix}_focus,3.5\n"
            ),
        )

        result = rule_queries.import_status_rules_csv(csv_file)

        self.assertFalse(result["success"])
        self.assertEqual(result["imported_count"], 0)
        self.assertEqual(result["errors"][0]["line"], 2)
