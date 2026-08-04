import io
import os
import unittest
import uuid

from werkzeug.datastructures import FileStorage

import backend.config as config
import backend.db as db
from backend.db import get_db_connection
from backend.table import init_db


def _with_connect_timeout(database_url):
    if "connect_timeout=" in database_url:
        return database_url

    separator = "&" if "?" in database_url else "?"
    return f"{database_url}{separator}connect_timeout=1"


def configure_database_connect_timeout():
    database_url = _with_connect_timeout(
        os.environ.get(
            "DATABASE_URL",
            config.DATABASE_URL,
        )
    )
    os.environ["DATABASE_URL"] = database_url
    config.DATABASE_URL = database_url
    db.DATABASE_URL = database_url


configure_database_connect_timeout()


_DATABASE_READY = None
_DATABASE_ERROR = None


def ensure_database_ready():
    global _DATABASE_READY
    global _DATABASE_ERROR

    if _DATABASE_READY is None:
        try:
            conn = get_db_connection()
            conn.close()
            init_db()
            _DATABASE_READY = True
        except Exception as error:
            _DATABASE_READY = False
            _DATABASE_ERROR = error

    if not _DATABASE_READY:
        raise unittest.SkipTest(f"database is not available: {_DATABASE_ERROR}")


class DatabaseIntegrationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ensure_database_ready()

    def setUp(self):
        self.prefix = f"itest_{self.__class__.__name__.lower()}_{uuid.uuid4().hex}"
        self.pattern = f"{self.prefix}%"
        self.cleanup_test_data()

    def tearDown(self):
        self.cleanup_test_data()

    def connect(self):
        return get_db_connection()

    def cleanup_test_data(self):
        conn = self.connect()
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
                OR category_id IN (
                    SELECT user_categories.id
                    FROM user_categories
                    JOIN master_categories
                    ON user_categories.master_category_id = master_categories.id
                    WHERE master_categories.category_name LIKE %s
                )
                """,
                (self.pattern, self.pattern, self.pattern),
            )
            cur.execute(
                """
                DELETE FROM user_achievements
                WHERE user_id IN (
                    SELECT id
                    FROM users
                    WHERE user_name LIKE %s
                )
                OR achievement_id IN (
                    SELECT id
                    FROM master_achievements
                    WHERE achievement_name LIKE %s
                    OR title_name LIKE %s
                    OR required_category_id IN (
                        SELECT id
                        FROM master_categories
                        WHERE category_name LIKE %s
                    )
                )
                """,
                (self.pattern, self.pattern, self.pattern, self.pattern),
            )
            cur.execute(
                """
                DELETE FROM user_statuses
                WHERE user_id IN (
                    SELECT id
                    FROM users
                    WHERE user_name LIKE %s
                )
                OR status_id IN (
                    SELECT id
                    FROM master_statuses
                    WHERE status_name LIKE %s
                )
                """,
                (self.pattern, self.pattern),
            )
            cur.execute(
                """
                DELETE FROM user_jobs
                WHERE user_id IN (
                    SELECT id
                    FROM users
                    WHERE user_name LIKE %s
                )
                OR job_id IN (
                    SELECT id
                    FROM master_jobs
                    WHERE job_name LIKE %s
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
                DELETE FROM job_requirements
                WHERE job_id IN (
                    SELECT id
                    FROM master_jobs
                    WHERE job_name LIKE %s
                )
                OR required_status_id IN (
                    SELECT id
                    FROM master_statuses
                    WHERE status_name LIKE %s
                )
                """,
                (self.pattern, self.pattern),
            )
            cur.execute(
                """
                DELETE FROM status_up_rules
                WHERE category_id IN (
                    SELECT id
                    FROM master_categories
                    WHERE category_name LIKE %s
                )
                OR status_id IN (
                    SELECT id
                    FROM master_statuses
                    WHERE status_name LIKE %s
                )
                """,
                (self.pattern, self.pattern),
            )
            cur.execute(
                """
                DELETE FROM master_achievements
                WHERE achievement_name LIKE %s
                OR title_name LIKE %s
                OR required_category_id IN (
                    SELECT id
                    FROM master_categories
                    WHERE category_name LIKE %s
                )
                """,
                (self.pattern, self.pattern, self.pattern),
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
                DELETE FROM master_jobs
                WHERE job_name LIKE %s
                """,
                (self.pattern,),
            )
            cur.execute(
                """
                DELETE FROM master_statuses
                WHERE status_name LIKE %s
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

    def execute(self, sql, params=()):
        conn = self.connect()
        cur = conn.cursor()

        try:
            cur.execute(sql, params)
            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

    def fetch_one(self, sql, params=()):
        conn = self.connect()
        cur = conn.cursor()

        try:
            cur.execute(sql, params)
            return cur.fetchone()

        finally:
            conn.close()

    def fetch_all(self, sql, params=()):
        conn = self.connect()
        cur = conn.cursor()

        try:
            cur.execute(sql, params)
            return cur.fetchall()

        finally:
            conn.close()

    def insert_and_return_id(self, sql, params=()):
        conn = self.connect()
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

    def insert_master_job(self, suffix="job", is_active=1, is_default=0):
        return self.insert_and_return_id(
            """
            INSERT INTO master_jobs(job_name, is_active, is_default)
            VALUES(%s, %s, %s)
            RETURNING id
            """,
            (f"{self.prefix}_{suffix}", is_active, is_default),
        )

    def insert_user(self, suffix="user", job_id=None, user_level=1, is_active=1, is_admin=0):
        if job_id is None:
            job_id = self.insert_master_job(f"{suffix}_job")

        return self.insert_and_return_id(
            """
            INSERT INTO users(
                user_name,
                password_hash,
                current_job_id,
                user_level,
                is_active,
                is_admin
            )
            VALUES(%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                f"{self.prefix}_{suffix}",
                "test-password-hash",
                job_id,
                user_level,
                is_active,
                is_admin,
            ),
        )

    def insert_master_category(self, suffix="category", is_active=1):
        return self.insert_and_return_id(
            """
            INSERT INTO master_categories(category_name, is_active)
            VALUES(%s, %s)
            RETURNING id
            """,
            (f"{self.prefix}_{suffix}", is_active),
        )

    def insert_user_category(self, user_id, master_category_id):
        return self.insert_and_return_id(
            """
            INSERT INTO user_categories(user_id, master_category_id)
            VALUES(%s, %s)
            RETURNING id
            """,
            (user_id, master_category_id),
        )

    def insert_master_status(
        self,
        suffix="status",
        status_type="front",
        default_value=10,
        is_active=1,
    ):
        return self.insert_and_return_id(
            """
            INSERT INTO master_statuses(
                status_name,
                status_type,
                default_value,
                is_active
            )
            VALUES(%s, %s, %s, %s)
            RETURNING id
            """,
            (f"{self.prefix}_{suffix}", status_type, default_value, is_active),
        )

    def insert_user_status(self, user_id, status_id, status_value=10):
        return self.insert_and_return_id(
            """
            INSERT INTO user_statuses(user_id, status_id, status_value)
            VALUES(%s, %s, %s)
            RETURNING id
            """,
            (user_id, status_id, status_value),
        )

    def insert_user_job(self, user_id, job_id):
        return self.insert_and_return_id(
            """
            INSERT INTO user_jobs(user_id, job_id)
            VALUES(%s, %s)
            RETURNING id
            """,
            (user_id, job_id),
        )

    def insert_status_rule(self, category_id, status_id, gain_per_hours=1, is_active=1):
        return self.insert_and_return_id(
            """
            INSERT INTO status_up_rules(
                category_id,
                status_id,
                gain_per_hours,
                is_active
            )
            VALUES(%s, %s, %s, %s)
            RETURNING id
            """,
            (category_id, status_id, gain_per_hours, is_active),
        )

    def insert_job_requirement(self, job_id, status_id, required_value=10, is_active=1):
        return self.insert_and_return_id(
            """
            INSERT INTO job_requirements(
                job_id,
                required_status_id,
                required_status_value,
                is_active
            )
            VALUES(%s, %s, %s, %s)
            RETURNING id
            """,
            (job_id, status_id, required_value, is_active),
        )

    def insert_master_achievement(
        self,
        category_id,
        suffix="achievement",
        required_hours=1,
        is_active=1,
    ):
        return self.insert_and_return_id(
            """
            INSERT INTO master_achievements(
                required_category_id,
                required_hours,
                achievement_name,
                title_name,
                is_active
            )
            VALUES(%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                category_id,
                required_hours,
                f"{self.prefix}_{suffix}",
                f"{self.prefix}_{suffix}_title",
                is_active,
            ),
        )

    def insert_user_achievement(self, user_id, achievement_id):
        return self.insert_and_return_id(
            """
            INSERT INTO user_achievements(user_id, achievement_id)
            VALUES(%s, %s)
            RETURNING id
            """,
            (user_id, achievement_id),
        )

    def insert_time_log(
        self,
        user_id,
        category_id,
        start_time="2026-08-03T10:00:00",
        end_time="2026-08-03T11:00:00",
        duration_seconds=3600,
    ):
        return self.insert_and_return_id(
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
            (user_id, category_id, start_time, end_time, duration_seconds),
        )

    def db_current_date_text(self):
        row = self.fetch_one("SELECT CURRENT_DATE::text AS today")
        return row["today"]


def make_csv_file(filename, text):
    return FileStorage(
        stream=io.BytesIO(text.encode("utf-8")),
        filename=filename,
    )
