import sqlite3
from flask import Flask
import os

app=Flask(__name__)

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_NAME=os.path.join(BASE_DIR,"rpg_table.db")

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

def get_user_by_name(user_name):
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
            ON master_jobs.id=users.current_job_id
            WHERE users.user_name=?""",(user_name,))
        
        user=cur.fetchone()
        return dict(user) if user else None

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
        

        

def create_user(user_name,password_hash):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT id
            FROM master_jobs
            WHERE is_default=1
            AND is_active=1""")

        default_job_id=cur.fetchone()[0]

        cur.execute("""
            INSERT INTO users(user_name,password_hash,current_job_id)
            VALUES(?,?,?)""",(user_name,password_hash,default_job_id))
        
        user_id=cur.lastrowid

        cur.execute("""
            SELECT id,
                    default_value
            FROM master_statuses
            WHERE is_active=1
            """)
        
        statuses=cur.fetchall()

        for status in statuses:
            cur.execute("""
                INSERT INTO user_statuses
                (user_id,status_id,status_value)
                VALUES(?,?,?)""",(user_id,
                                status["id"],
                                status["default_value"])
            )

        cur.execute("""
            SELECT id
            FROM master_jobs
            WHERE is_default=1
            AND is_active=1""")

        job_id=cur.fetchone()[0]
                
        cur.execute("""
            INSERT INTO user_jobs(user_id,job_id)
            VALUES(?,?)
            """,(user_id,job_id))
        
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()