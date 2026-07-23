import sqlite3
from flask import Flask
import os

app=Flask(__name__)

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_NAME=os.path.join(BASE_DIR,"rpg_table.db")

def get_time_logs(user_id):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT master_categories.category_name,
                    time_logs.start_time,
                    time_logs.end_time,
                    time_logs.duration_seconds
            FROM time_logs
            JOIN user_categories
            ON time_logs.category_id=user_categories.id
            JOIN master_categories
            ON user_categories.master_category_id=master_categories.id
            WHERE time_logs.user_id=? AND master_categories.is_active=1
            """,(user_id,))
        
        logs=cur.fetchall()
        return logs

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
    

def get_user_statuses(user_id):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT  user_statuses.id AS status_id, 
                    status_name,
                    status_value,
                    status_type
            FROM user_statuses
            JOIN users
            ON users.id=use_statuses.user_id
            JOIN master_statuses
            ON master_statuses.id=user_statuses.status_id
            WHERE user_id=?
            ORDER BY master_statuses.id""",(user_id,))
        
        user_status_row=cur.fetchall()
        return user_status_row

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
    

def get_user_by_id(user_id):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT users.id AS id,
                    user_name,
                    password_hash,
                    job_name AS current_job_name,
                    user_level,
                    is_admin
            FROM users
            JOIN master_jobs
            ON users.current_job_id = master_jobs.id
            WHERE users.id=?""",(user_id,))
        
        user=cur.fetchone()
        return dict(user) if user else None

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
        
def get_user_achievements(user_id):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT  
                master_achievements.achievement_name,
                master_achievements.title_name            
            FROM user_achievements
            JOIN master_achievements
            ON user_achievements.achievement_id=master_achievements.id
            WHERE user_achievements.user_id=? AND master_achievements.is_active=1
            ORDER BY master_achievements.id ASC  """,(user_id,))
        
        user_achievements=cur.fetchall()
        return user_achievements

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
    

def get_user_jobs(user_id):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT  user_jobs.job_id AS job_id,
                    master_jobs.job_name AS job_name
            FROM user_jobs
            JOIN master_jobs
            ON user_jobs.job_id=master_jobs.id
            WHERE user_jobs.user_id=? 
            AND master_jobs.is_active=1
            """,(user_id,))
        
        user_jobs=cur.fetchone() 
        return user_jobs

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    