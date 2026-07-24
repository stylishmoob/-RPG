import sqlite3
from flask import Flask
import os

app=Flask(__name__)

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_NAME=os.path.join(BASE_DIR,"rpg_table.db")

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

def check_user_job(user_id):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT status_id,
                    status_value
            FROM user_statuses
            WHERE user_id=?
            """,(user_id,))
        
        user_status={
            row["status_id"]:row["status_value"]
            for row in cur.fetchall()
        }

        cur.execute("""
            SELECT  
                    job_id,
                    required_status_id,
                    required_status_value
                FROM job_requirements
                WHERE is_active=1  
                ORDER BY job_id,id
            """)
        rows=cur.fetchall()

        requirements_by_job={}

        for row in rows:
            job_id = row["job_id"]

            if job_id not in requirements_by_job:
                requirements_by_job[job_id]=[]
            
            requirements_by_job[job_id].append(row)
        
        new_job_ids =[]
        
        for job_id,requirements in requirements_by_job.items():
            ok = True
            for req in requirements:
                user_value=user_status.get(req["status_id"],0)

                if user_value < req["required_value"]:
                    ok = False
                    break

            if ok:
                cur.execute("""
                    INSERT OR IGNORE INTO user_jobs(user_id,job_id)
                    VALUES (?,?)""",(user_id,job_id))
                
                if cur.rowcount > 0:
                    new_job_ids.append(job_id)
            
        conn.commit()

        # return new_job_ids
    
    except Exception:
        conn.rollback()
        raise

    finally:
            conn.close()