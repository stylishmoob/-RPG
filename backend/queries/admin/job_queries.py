from flask import Flask
import csv
import io

from backend.db import get_db_connection

from backend.queries.admin.status_queries import(
    get_status_id_by_name,
)

app=Flask(__name__)

def get_master_jobs():
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT id,
                    job_name,
                    is_active,
                    is_default
            FROM master_jobs
            """)
        
        master_jobs=cur.fetchall()
        return master_jobs

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

        

def get_job_requirements():
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT job_requirements.id AS id,
                    job_id, 
                    required_status_id,
                    status_name AS required_status_name,
                    required_status_value,
                    job_requirements.is_active AS is_active
            FROM job_requirements
            JOIN master_statuses
            ON required_status_id = master_statuses.id
            """)
        
        job_requirements=cur.fetchall()
        return job_requirements

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    

def add_admin_job(job_name,requirements):
    conn=get_db_connection()
    cur=conn.cursor()
    try:
        job_id=add_master_job(cur,job_name)
        add_master_jobrequirements(cur,job_id,requirements)

        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

def add_master_job(cur,job_name):
    cur.execute("""
        INSERT INTO master_jobs
        (job_name)
        VALUES(%s)
        RETURNING id
        """,(job_name,))
    
    job_id=cur.fetchone()["id"]

    return job_id

def add_master_jobrequirements(cur,job_id,requirements):
    for req in requirements:
        cur.execute("""
            INSERT INTO job_requirements
            (job_id,required_status_id,required_status_value)
            VALUES(%s,%s,%s)
            """,(job_id,req["statusId"],req["requiredValue"],))

def edit_admin_job(job_id,job_name,is_active,is_default,requirements):
    conn=get_db_connection()
    cur=conn.cursor()
    try:
        edit_master_job(cur,job_id,job_name,is_active,is_default)
        edit_job_requirement(cur,job_id,requirements)

        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

def edit_master_job(cur,job_id,job_name,is_active,is_default):
    cur.execute("""
        UPDATE master_jobs
        SET job_name=%s,
            is_active=%s,
            is_default=%s
        WHERE id=%s""",(job_name,int(is_active),int(is_default),job_id))
    
def edit_job_requirement(cur,job_id,requirements):
    for req in requirements:
        cur.execute("""
        UPDATE job_requirements
        SET required_status_id=%s,required_status_value=%s,is_active=%s
        WHERE id=%s
        AND job_id=%s""",(
            req["statusId"],
            req["requiredValue"],
            int(req["isActive"]),
            req["id"],
            job_id,
        ))


def delete_admin_job(job_id):
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT id
            FROM master_jobs
            WHERE id<>%s
            AND is_active=1
            ORDER BY is_default DESC,id
            LIMIT 1""",(job_id,))
        fallback_job=cur.fetchone()

        cur.execute("""
            SELECT COUNT(*) AS user_count
            FROM users
            WHERE current_job_id=%s""",(job_id,))
        current_job_user_count=cur.fetchone()["user_count"]

        if current_job_user_count > 0 and fallback_job is None:
            raise ValueError("削除後に設定できる職業がありません")

        if fallback_job is not None:
            cur.execute("""
                UPDATE users
                SET current_job_id=%s
                WHERE current_job_id=%s""",(fallback_job["id"],job_id))
            updated_current_jobs=cur.rowcount
        else:
            updated_current_jobs=0

        cur.execute("""
            DELETE FROM job_requirements
            WHERE job_id=%s""",(job_id,))
        deleted_job_requirements=cur.rowcount

        cur.execute("""
            DELETE FROM user_jobs
            WHERE job_id=%s""",(job_id,))
        deleted_user_jobs=cur.rowcount

        cur.execute("""
            DELETE FROM master_jobs
            WHERE id=%s""",(job_id,))
        deleted_jobs=cur.rowcount

        conn.commit()

        return {
            "deleted": deleted_jobs > 0,
            "job_id": job_id,
            "deleted_job_requirements": deleted_job_requirements,
            "deleted_user_jobs": deleted_user_jobs,
            "updated_current_jobs": updated_current_jobs,
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def delete_job_requirement(requirement_id):
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            DELETE FROM job_requirements
            WHERE id=%s""",(requirement_id,))
        deleted_job_requirements=cur.rowcount

        conn.commit()

        return {
            "deleted": deleted_job_requirements > 0,
            "requirement_id": requirement_id,
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def import_jobs_csv(csv_file):
    if csv_file is None:
        return ({
            "success": False,
            "message": "CSVファイルがありません",
        })

    if csv_file.filename == "":
        return ({
            "success": False,
            "message": "ファイルが選択されていません",
        })

    if not csv_file.filename.lower().endswith(".csv"):
        return ({
            "success": False,
            "message": "CSVファイルを選択してください",
        })
    
    text_file = io.TextIOWrapper(
            csv_file.stream,
            encoding="utf-8-sig",
            newline="",
        )

    reader = csv.DictReader(text_file)

    required_columns = {
        "job_name",
        "required_status_name",
        "required_status_value",
    }

    if reader.fieldnames is None:
        return ({
            "success": False,
            "message": "CSVのヘッダーがありません",
        })

    missing_columns = required_columns - set(reader.fieldnames)

    if missing_columns:
        return ({
            "success": False,
            "message": "必要な列がありません",
            "missing_columns": list(missing_columns),
        })

    jobs_data={}
    errors = []

    for line_number, row in enumerate(reader, start=2):
        job_name = row["job_name"].strip()
        required_status_name = row["required_status_name"].strip()
        required_status_value = row["required_status_value"].strip()

        if not job_name:
            errors.append({
                "line": line_number,
                "message": "job_nameが空です",
            })
            continue

        if not required_status_name:
            errors.append({
                "line": line_number,
                "message": "required_status_nameが空です",
            })
            continue

        if not required_status_value:
            errors.append({
                "line": line_number,
                "message": "required_status_valueが空です",
            })
            continue


        try:
            required_status_value=int(required_status_value)

        except ValueError:
            errors.append({
                "line":line_number,
                "message":"required_status_valueは整数で入力してください",
            })
            continue

        status_id=get_status_id_by_name(required_status_name)

        if status_id is None:
            errors.append({
                "line": line_number,
                "message": f"ステータス「{required_status_name}」が存在しません",
            })
            continue

        if job_name not in jobs_data:
            jobs_data[job_name]=[]

        jobs_data[job_name].append({
            "required_status_id":status_id,
            "required_status_value":required_status_value,
        })

    conn=get_db_connection()
    cur=conn.cursor()
    
    try:
        imported_count =0

        for job_name,requirements in jobs_data.items():
            job_id =import_master_job(cur,job_name)

            for requirement in requirements:
                import_job_requirement(
                    cur,
                    job_id,
                    requirement["required_status_id"],
                    requirement["required_status_value"]
                )
                imported_count +=1

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
    
    return ({
        "success": True,
        "message": f"{imported_count}件追加しました",
        "imported_count": imported_count,
        "errors": [],
    })

def import_master_job(cur,job_name):
    cur.execute("""
        INSERT INTO master_jobs
        (job_name)
        VALUES(%s)
        ON CONFLICT (job_name) DO NOTHING
        RETURNING id
        """,(job_name,))

    row=cur.fetchone()

    if row is not None:
        return row["id"]

    cur.execute("""
        SELECT id
        FROM master_jobs
        WHERE job_name=%s
        """,(job_name,))

    return cur.fetchone()["id"]

def import_job_requirement(cur,job_id,status_id,status_value):
    cur.execute("""
        INSERT INTO job_requirements
        (job_id,
        required_status_id,
        required_status_value)
        VALUES(%s,%s,%s)
        """,(job_id,status_id,status_value))
