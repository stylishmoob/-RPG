from flask import Flask

from backend.db import get_db_connection

app=Flask(__name__)

def get_user_statuses(user_id):
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT  user_statuses.id AS status_id, 
                    status_name,
                    status_value,
                    status_type
            FROM user_statuses
            JOIN users
            ON users.id=user_statuses.user_id
            JOIN master_statuses
            ON master_statuses.id=user_statuses.status_id
            WHERE user_id=%s
            ORDER BY master_statuses.id""",(user_id,))
        
        user_status_row=cur.fetchall()
        return user_status_row

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
    

def get_user_by_id(user_id):
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT users.id AS id,
                    user_name,
                    password_hash,
                    current_job_id,
                    job_name AS current_job_name,
                    user_level,
                    is_admin
            FROM users
            JOIN master_jobs
            ON users.current_job_id = master_jobs.id
            WHERE users.id=%s""",(user_id,))
        
        user=cur.fetchone()
        return dict(user) if user else None

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def status_cir(category_id,duration_seconds,user_id):
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT sur.status_id,
                    sur.gain_per_hours
            FROM user_categories 
            JOIN status_up_rules sur
                ON user_categories.master_category_id = sur.category_id
            WHERE user_categories.id=%s""",(category_id,))

        rules=cur.fetchall()

        for rule in rules:
            gain=duration_seconds / 3600 * rule["gain_per_hours"]

            cur.execute("""
                UPDATE user_statuses
                SET status_value=status_value+%s
                WHERE status_id=%s AND user_id=%s""",
                (gain,rule["status_id"],user_id))
        #経験値効率設定変更可
        exp=(duration_seconds / 3600 )*(360) 

        cur.execute("""
            UPDATE users
            SET user_level=user_level+%s
            WHERE users.id=%s""",(exp,user_id))
            
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
