import sqlite3
from flask import Flask
import os
import csv
import io

from backend.queries.admin.status_queries import(
    get_status_id_by_name,
)

app=Flask(__name__)

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_NAME=os.path.join(BASE_DIR,"rpg_table.db")

def get_master_jobs():
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
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
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
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
    conn=sqlite3.connect(DB_NAME)
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
        VALUES(?)""",(job_name,))
    
    job_id=cur.lastrowid

    return job_id

def add_master_jobrequirements(cur,job_id,requirements):
    for req in requirements:
        cur.execute("""
            INSERT INTO job_requirements
            (job_id,required_status_id,required_status_value)
            VALUES(?,?,?)
            """,(job_id,req["statusId"],req["requiredValue"],))

def edit_admin_job(job_id,job_name,is_active,is_default,requirements):
    conn=sqlite3.connect(DB_NAME)
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
        SET job_name=?,
            is_active=?,
            is_default=?
        WHERE job_id=?""",(job_name,is_active,is_default,job_id))
    
def edit_job_requirement(cur,job_id,requirements):
    for req in requirements:
        cur.execute("""
        UPDATE job_requirements
        SET required_status_id=?,required_status_value=?,is_active=?
        WHERE id=?
        AND job_id=?""",(
            req["statusId"],
            req["statusValue"],
            req["isActive"],
            req["id"],
            job_id,
        ))


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

    conn=sqlite3.connect(DB_NAME)
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
        VALUES=(?)""",(job_name,))

    return cur.lastrowid

def import_job_requirement(cur,job_id,status_id,status_value):
    cur.execute("""
        INSERT INTO job_requirements
        (job_id,
        required_status_id,
        required_status_value)
        VALUES=(?,?,?)""",(job_id,status_id,status_value))