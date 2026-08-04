from backend.queries import time_logs_queries
from backend.tests.integration.db_helpers import DatabaseIntegrationTestCase


class TimeLogsQueriesIntegrationTestCase(DatabaseIntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.job_id = self.insert_master_job()
        self.user_id = self.insert_user(job_id=self.job_id)
        self.category_id = self.insert_master_category("study", is_active=1)
        self.user_category_id = self.insert_user_category(self.user_id, self.category_id)

    def test_save_time_logs_persists_log_and_get_time_logs_reads_it(self):
        time_logs_queries.save_time_logs(
            self.user_id,
            self.user_category_id,
            "2026-08-03T09:00:00",
            "2026-08-03T10:00:00",
            3600,
        )

        rows = time_logs_queries.get_time_logs(self.user_id)
        matching_rows = [
            row for row in rows
            if row["category_name"] == f"{self.prefix}_study"
        ]

        self.assertEqual(len(matching_rows), 1)
        self.assertEqual(matching_rows[0]["duration_seconds"], 3600)

    def test_get_today_logs_returns_current_day_logs(self):
        today = self.db_current_date_text()
        self.insert_time_log(
            self.user_id,
            self.user_category_id,
            start_time=f"{today}T09:00:00",
            end_time=f"{today}T10:00:00",
            duration_seconds=3600,
        )
        self.insert_time_log(
            self.user_id,
            self.user_category_id,
            start_time="2000-01-01T09:00:00",
            end_time="2000-01-01T10:00:00",
            duration_seconds=3600,
        )

        rows = time_logs_queries.get_today_logs(self.user_id)
        matching_rows = [
            row for row in rows
            if row["category_name"] == f"{self.prefix}_study"
        ]

        self.assertEqual(len(matching_rows), 1)
        self.assertEqual(matching_rows[0]["start_time"], "09:00:00")
        self.assertEqual(matching_rows[0]["end_time"], "10:00:00")

    def test_category_and_daily_summary_aggregate_active_categories(self):
        inactive_category_id = self.insert_master_category("inactive", is_active=0)
        inactive_user_category_id = self.insert_user_category(
            self.user_id,
            inactive_category_id,
        )
        self.insert_time_log(
            self.user_id,
            self.user_category_id,
            start_time="2026-08-03T09:00:00",
            end_time="2026-08-03T10:00:00",
            duration_seconds=3600,
        )
        self.insert_time_log(
            self.user_id,
            self.user_category_id,
            start_time="2026-08-03T11:00:00",
            end_time="2026-08-03T11:30:00",
            duration_seconds=1800,
        )
        self.insert_time_log(
            self.user_id,
            inactive_user_category_id,
            start_time="2026-08-03T12:00:00",
            end_time="2026-08-03T13:00:00",
            duration_seconds=3600,
        )

        category_rows = time_logs_queries.get_category_summary("all", self.user_id)
        daily_rows = time_logs_queries.get_daily_summary("all", self.user_id)
        category_by_name = {row["category_name"]: row for row in category_rows}
        daily_by_name = {row["category_name"]: row for row in daily_rows}

        self.assertEqual(
            category_by_name[f"{self.prefix}_study"]["category_total_seconds"],
            5400,
        )
        self.assertEqual(
            daily_by_name[f"{self.prefix}_study"]["daily_total_seconds"],
            5400,
        )
        self.assertNotIn(f"{self.prefix}_inactive", category_by_name)
        self.assertNotIn(f"{self.prefix}_inactive", daily_by_name)

    def test_check_period_returns_postgresql_filters(self):
        self.assertEqual(
            time_logs_queries.check_period("today"),
            "AND time_logs.start_time::timestamp::date=CURRENT_DATE",
        )
        self.assertIn("INTERVAL '6 days'", time_logs_queries.check_period("7days"))
        self.assertIn("EXTRACT(DOW FROM CURRENT_DATE)", time_logs_queries.check_period("week"))
        self.assertIn("'YYYY-MM'", time_logs_queries.check_period("month"))
        self.assertIn("'YYYY'", time_logs_queries.check_period("year"))
        self.assertEqual(time_logs_queries.check_period("all"), "")
