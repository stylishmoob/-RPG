import sqlite3
from flask import Flask

from backend.config import DB_NAME

app=Flask(__name__)

def get_admin_users():
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT users.id AS id,
                    users.user_name AS user_name,
                    users.user_level AS user_level,
                    master_jobs.job_name AS current_job_name,
                    users.is_admin AS is_admin,
                    users.is_active AS is_active
            FROM users
            LEFT JOIN master_jobs
            ON users.current_job_id = master_jobs.id
            ORDER BY users.id
            """)

        admin_users=cur.fetchall()
        return admin_users

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def edit_admin_user_active(user_id,is_active):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    try:
        cur.execute("""
            UPDATE users
            SET is_active=?
            WHERE id=?
            """,(is_active,user_id))

        updated_users=cur.rowcount
        conn.commit()

        return {
            "updated": updated_users > 0,
            "user_id": user_id,
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def reset_admin_user_data(user_id):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    try:
        cur.execute("BEGIN")

        cur.execute("""
            SELECT id
            FROM users
            WHERE id=?
            """,(user_id,))

        if cur.fetchone() is None:
            raise ValueError("対象ユーザーが存在しません")

        cur.execute("""
            SELECT id
            FROM master_jobs
            WHERE is_default=1
            AND is_active=1
            ORDER BY id
            LIMIT 1
            """)

        default_job=cur.fetchone()

        if default_job is None:
            raise ValueError("デフォルト職業が存在しません")

        default_job_id=default_job["id"]

        cur.execute("""
            DELETE FROM time_logs
            WHERE user_id=?
            """,(user_id,))
        deleted_time_logs=cur.rowcount

        cur.execute("""
            DELETE FROM user_categories
            WHERE user_id=?
            """,(user_id,))
        deleted_user_categories=cur.rowcount

        cur.execute("""
            DELETE FROM user_statuses
            WHERE user_id=?
            """,(user_id,))
        deleted_user_statuses=cur.rowcount

        cur.execute("""
            DELETE FROM user_jobs
            WHERE user_id=?
            """,(user_id,))
        deleted_user_jobs=cur.rowcount

        cur.execute("""
            DELETE FROM user_achievements
            WHERE user_id=?
            """,(user_id,))
        deleted_user_achievements=cur.rowcount

        cur.execute("""
            UPDATE users
            SET user_level=1,
                current_job_id=?
            WHERE id=?
            """,(default_job_id,user_id))
        updated_users=cur.rowcount

        cur.execute("""
            INSERT INTO user_statuses
            (user_id,status_id,status_value)
            SELECT ?,id,default_value
            FROM master_statuses
            WHERE is_active=1
            """,(user_id,))
        inserted_user_statuses=cur.rowcount

        cur.execute("""
            INSERT INTO user_jobs
            (user_id,job_id)
            VALUES(?,?)
            """,(user_id,default_job_id))
        inserted_user_jobs=cur.rowcount

        conn.commit()

        return {
            "reset": True,
            "user_id": user_id,
            "default_job_id": default_job_id,
            "updated_users": updated_users,
            "deleted_time_logs": deleted_time_logs,
            "deleted_user_categories": deleted_user_categories,
            "deleted_user_statuses": deleted_user_statuses,
            "deleted_user_jobs": deleted_user_jobs,
            "deleted_user_achievements": deleted_user_achievements,
            "inserted_user_statuses": inserted_user_statuses,
            "inserted_user_jobs": inserted_user_jobs,
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def delete_admin_user(user_id):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    try:
        cur.execute("BEGIN")

        cur.execute("""
            SELECT id
            FROM users
            WHERE id=?
            """,(user_id,))

        if cur.fetchone() is None:
            raise ValueError("対象ユーザーが存在しません")

        cur.execute("""
            DELETE FROM time_logs
            WHERE user_id=?
            """,(user_id,))
        deleted_time_logs=cur.rowcount

        cur.execute("""
            DELETE FROM user_categories
            WHERE user_id=?
            """,(user_id,))
        deleted_user_categories=cur.rowcount

        cur.execute("""
            DELETE FROM user_statuses
            WHERE user_id=?
            """,(user_id,))
        deleted_user_statuses=cur.rowcount

        cur.execute("""
            DELETE FROM user_jobs
            WHERE user_id=?
            """,(user_id,))
        deleted_user_jobs=cur.rowcount

        cur.execute("""
            DELETE FROM user_achievements
            WHERE user_id=?
            """,(user_id,))
        deleted_user_achievements=cur.rowcount

        cur.execute("""
            DELETE FROM users
            WHERE id=?
            """,(user_id,))
        deleted_users=cur.rowcount

        conn.commit()

        return {
            "deleted": deleted_users > 0,
            "user_id": user_id,
            "deleted_users": deleted_users,
            "deleted_time_logs": deleted_time_logs,
            "deleted_user_categories": deleted_user_categories,
            "deleted_user_statuses": deleted_user_statuses,
            "deleted_user_jobs": deleted_user_jobs,
            "deleted_user_achievements": deleted_user_achievements,
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
