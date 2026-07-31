from flask import Flask

from backend.db import get_db_connection

app=Flask(__name__)

def get_user_jobs(user_id):
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT  user_jobs.job_id AS job_id,
                    master_jobs.job_name AS job_name
            FROM user_jobs
            JOIN master_jobs
            ON user_jobs.job_id=master_jobs.id
            WHERE user_jobs.user_id=%s
            AND master_jobs.is_active=1
            """,(user_id,))
        
        user_jobs=cur.fetchall() 
        return user_jobs

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def update_current_job(user_id,current_job_id):
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT 1
            FROM user_jobs
            JOIN master_jobs
            ON user_jobs.job_id=master_jobs.id
            WHERE user_jobs.user_id=%s
            AND user_jobs.job_id=%s
            AND master_jobs.is_active=1
            """,(user_id,current_job_id))

        if cur.fetchone() is None:
            conn.rollback()
            return {
                "updated": False,
                "reason": "job_not_owned",
            }

        cur.execute("""
            UPDATE users
            SET current_job_id=%s
            WHERE id=%s
            """,(current_job_id,user_id))

        conn.commit()

        return {
            "updated": cur.rowcount > 0,
            "current_job_id": current_job_id,
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def check_user_job(user_id):
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT status_id,
                    status_value
            FROM user_statuses
            WHERE user_id=%s
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
                user_value=user_status.get(req["required_status_id"],0)

                if user_value < req["required_status_value"]:
                    ok = False
                    break

            if ok:
                cur.execute("""
                    INSERT INTO user_jobs(user_id,job_id)
                    VALUES (%s,%s)
                    ON CONFLICT (user_id,job_id) DO NOTHING
                    """,(user_id,job_id))
                
                if cur.rowcount > 0:
                    new_job_ids.append(job_id)
            
        conn.commit()

        return new_job_ids
    
    except Exception:
        conn.rollback()
        raise

    finally:
            conn.close()
