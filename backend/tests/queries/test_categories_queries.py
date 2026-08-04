import unittest
import uuid

from psycopg import errors

from backend.tests.integration.db_helpers import (
    configure_database_connect_timeout,
    ensure_database_ready,
)

configure_database_connect_timeout()

from backend.db import get_db_connection
from backend.queries import categories_queries
from backend.table import init_db


class CategoriesQueriesIntegrationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ensure_database_ready()

    def setUp(self):
        self.prefix = f"itest_categories_{uuid.uuid4().hex}"
        self.pattern = f"{self.prefix}%"
        self._cleanup_test_data()
        self._create_fixture()

    def tearDown(self):
        self._cleanup_test_data()

    def _connect(self):
        return get_db_connection()

    def _cleanup_test_data(self):
        conn = self._connect()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                DELETE FROM time_logs
                WHERE user_id IN (
                    SELECT id
                    FROM users
                    WHERE user_name LIKE %s
                )
                OR category_id IN (
                    SELECT user_categories.id
                    FROM user_categories
                    JOIN users
                    ON user_categories.user_id = users.id
                    WHERE users.user_name LIKE %s
                )
                """,
                (self.pattern, self.pattern),
            )
            cur.execute(
                """
                DELETE FROM user_categories
                WHERE user_id IN (
                    SELECT id
                    FROM users
                    WHERE user_name LIKE %s
                )
                OR master_category_id IN (
                    SELECT id
                    FROM master_categories
                    WHERE category_name LIKE %s
                )
                """,
                (self.pattern, self.pattern),
            )
            cur.execute(
                """
                DELETE FROM user_statuses
                WHERE user_id IN (
                    SELECT id
                    FROM users
                    WHERE user_name LIKE %s
                )
                """,
                (self.pattern,),
            )
            cur.execute(
                """
                DELETE FROM user_achievements
                WHERE user_id IN (
                    SELECT id
                    FROM users
                    WHERE user_name LIKE %s
                )
                """,
                (self.pattern,),
            )
            cur.execute(
                """
                DELETE FROM user_jobs
                WHERE user_id IN (
                    SELECT id
                    FROM users
                    WHERE user_name LIKE %s
                )
                """,
                (self.pattern,),
            )
            cur.execute(
                """
                DELETE FROM users
                WHERE user_name LIKE %s
                """,
                (self.pattern,),
            )
            cur.execute(
                """
                DELETE FROM job_requirements
                WHERE job_id IN (
                    SELECT id
                    FROM master_jobs
                    WHERE job_name LIKE %s
                )
                """,
                (self.pattern,),
            )
            cur.execute(
                """
                DELETE FROM master_jobs
                WHERE job_name LIKE %s
                """,
                (self.pattern,),
            )
            cur.execute(
                """
                DELETE FROM status_up_rules
                WHERE category_id IN (
                    SELECT id
                    FROM master_categories
                    WHERE category_name LIKE %s
                )
                """,
                (self.pattern,),
            )
            cur.execute(
                """
                DELETE FROM master_achievements
                WHERE required_category_id IN (
                    SELECT id
                    FROM master_categories
                    WHERE category_name LIKE %s
                )
                """,
                (self.pattern,),
            )
            cur.execute(
                """
                DELETE FROM master_categories
                WHERE category_name LIKE %s
                """,
                (self.pattern,),
            )
            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

    def _create_fixture(self):
        self.job_id = self._insert_job("job")
        self.user_id = self._insert_user("user")
        self.other_user_id = self._insert_user("other_user")
        self.active_category_id = self._insert_master_category("active", 1)
        self.inactive_category_id = self._insert_master_category("inactive", 0)
        self.other_category_id = self._insert_master_category("other", 1)

        self.active_user_category_id = self._insert_user_category(
            self.user_id,
            self.active_category_id,
        )
        self.inactive_user_category_id = self._insert_user_category(
            self.user_id,
            self.inactive_category_id,
        )
        self.other_user_category_id = self._insert_user_category(
            self.other_user_id,
            self.other_category_id,
        )

    def _insert_job(self, suffix):
        return self._insert_and_return_id(
            """
            INSERT INTO master_jobs(job_name, is_active, is_default)
            VALUES(%s, 1, 0)
            RETURNING id
            """,
            (f"{self.prefix}_{suffix}",),
        )

    def _insert_user(self, suffix):
        return self._insert_and_return_id(
            """
            INSERT INTO users(user_name, password_hash, current_job_id, user_level)
            VALUES(%s, %s, %s, 1)
            RETURNING id
            """,
            (f"{self.prefix}_{suffix}", "test-password-hash", self.job_id),
        )

    def _insert_master_category(self, suffix, is_active):
        return self._insert_and_return_id(
            """
            INSERT INTO master_categories(category_name, is_active)
            VALUES(%s, %s)
            RETURNING id
            """,
            (f"{self.prefix}_{suffix}", is_active),
        )

    def _insert_user_category(self, user_id, master_category_id):
        return self._insert_and_return_id(
            """
            INSERT INTO user_categories(user_id, master_category_id)
            VALUES(%s, %s)
            RETURNING id
            """,
            (user_id, master_category_id),
        )

    def _insert_time_log(self, user_id, category_id):
        return self._insert_and_return_id(
            """
            INSERT INTO time_logs(
                user_id,
                category_id,
                start_time,
                end_time,
                duration_seconds
            )
            VALUES(%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                user_id,
                category_id,
                "2026-08-03T10:00:00",
                "2026-08-03T11:00:00",
                3600,
            ),
        )

    def _insert_and_return_id(self, sql, params):
        conn = self._connect()
        cur = conn.cursor()

        try:
            cur.execute(sql, params)
            row = cur.fetchone()
            conn.commit()
            return row["id"]

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

    def _fetch_one(self, sql, params):
        conn = self._connect()
        cur = conn.cursor()

        try:
            cur.execute(sql, params)
            return cur.fetchone()

        finally:
            conn.close()

    def test_get_user_categories_reads_only_active_categories_for_user(self):
        rows = categories_queries.get_user_categories(self.user_id)
        rows_by_name = {row["category_name"]: row for row in rows}

        self.assertIn(f"{self.prefix}_active", rows_by_name)
        self.assertEqual(
            rows_by_name[f"{self.prefix}_active"]["category_id"],
            self.active_user_category_id,
        )
        self.assertNotIn(f"{self.prefix}_inactive", rows_by_name)
        self.assertNotIn(f"{self.prefix}_other", rows_by_name)

    def test_get_user_master_categories_reads_only_active_master_categories(self):
        rows = categories_queries.get_user_master_categories()
        names = {row["category_name"] for row in rows}

        self.assertIn(f"{self.prefix}_active", names)
        self.assertIn(f"{self.prefix}_other", names)
        self.assertNotIn(f"{self.prefix}_inactive", names)

    def test_add_user_category_persists_relation_and_ignores_duplicate(self):
        new_category_id = self._insert_master_category("new", 1)

        categories_queries.add_user_category(self.user_id, new_category_id)
        categories_queries.add_user_category(self.user_id, new_category_id)

        row = self._fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM user_categories
            WHERE user_id=%s
            AND master_category_id=%s
            """,
            (self.user_id, new_category_id),
        )
        self.assertEqual(row["count"], 1)

    def test_add_user_category_rolls_back_when_foreign_key_fails(self):
        missing_master_category_id = -1

        with self.assertRaises(errors.ForeignKeyViolation):
            categories_queries.add_user_category(
                self.user_id,
                missing_master_category_id,
            )

        row = self._fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM user_categories
            WHERE user_id=%s
            AND master_category_id=%s
            """,
            (self.user_id, missing_master_category_id),
        )
        self.assertEqual(row["count"], 0)

    def test_delete_user_category_removes_time_logs_and_user_category(self):
        time_log_id = self._insert_time_log(
            self.user_id,
            self.active_user_category_id,
        )

        categories_queries.delete_user_category(
            self.user_id,
            self.active_user_category_id,
        )

        user_category = self._fetch_one(
            """
            SELECT id
            FROM user_categories
            WHERE id=%s
            """,
            (self.active_user_category_id,),
        )
        time_log = self._fetch_one(
            """
            SELECT id
            FROM time_logs
            WHERE id=%s
            """,
            (time_log_id,),
        )

        self.assertIsNone(user_category)
        self.assertIsNone(time_log)

    def test_edit_user_category_persists_new_master_category(self):
        new_category_id = self._insert_master_category("edited", 1)

        categories_queries.edit_user_category(
            self.user_id,
            new_category_id,
            self.active_user_category_id,
        )

        row = self._fetch_one(
            """
            SELECT master_category_id
            FROM user_categories
            WHERE id=%s
            AND user_id=%s
            """,
            (self.active_user_category_id, self.user_id),
        )
        self.assertEqual(row["master_category_id"], new_category_id)


if __name__ == "__main__":
    unittest.main()
