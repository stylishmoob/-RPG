import sqlite3
from flask import Flask
import os

app=Flask(__name__)

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_NAME=os.path.join(BASE_DIR,"rpg_table.db")
    

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

def status_cir(category_id,duration_seconds,user_id):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT sur.status_id,
                    sur.gain_per_hours
            FROM user_categories 
            JOIN status_up_rules sur
                ON user_categories.master_category_id = sur.category_id
            WHERE user_categories.id=?""",(category_id,))

        rules=cur.fetchall()

        for status_id,gain_per_hours in rules:
            gain=duration_seconds / 3600 * gain_per_hours

            cur.execute("""
                UPDATE user_statuses
                SET status_value=status_value+?
                WHERE status_id=? AND user_id=?""",
                (gain,status_id,user_id))
        #経験値効率設定変更可
        exp=(duration_seconds / 3600 )*(360) 

        cur.execute("""
            UPDATE users
            SET user_level=user_level+?
            WHERE users.id=?""",(exp,user_id))
            
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()




    