from flask import Flask
import csv
import io

from backend.db import get_db_connection

app=Flask(__name__)

def get_master_statuses():
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT * FROM master_statuses""")
        
        master_statuses=cur.fetchall()
        return master_statuses

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
        

def add_master_status(status_name,default_value,status_type):
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            INSERT INTO master_statuses
            (status_name,default_value,status_type)
            VALUES(%s,%s,%s)""",(status_name,default_value,status_type))
        
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def edit_master_status(status_id,status_name,default_value,status_type,is_active):
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            UPDATE master_statuses
            SET status_name=%s,default_value=%s,status_type=%s,is_active=%s
            WHERE id=%s""",(status_name,default_value,status_type,int(is_active),status_id))
        
        conn.commit()

    except Exception:
        conn.rollback()

    finally:
        conn.close()

def delete_master_status(status_id):
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT id
            FROM master_statuses
            WHERE id=%s
            """,(status_id,))

        status = cur.fetchone()

        if status is None:
            conn.rollback()
            return {
                "deleted": False,
                "status_id": status_id,
            }

        cur.execute("""
            DELETE FROM status_up_rules
            WHERE status_id=%s
            """,(status_id,))
        deleted_status_rules = cur.rowcount

        cur.execute("""
            DELETE FROM job_requirements
            WHERE required_status_id=%s
            """,(status_id,))
        deleted_job_requirements = cur.rowcount

        cur.execute("""
            DELETE FROM user_statuses
            WHERE status_id=%s
            """,(status_id,))
        deleted_user_statuses = cur.rowcount

        cur.execute("""
            DELETE FROM master_statuses
            WHERE id=%s
            """,(status_id,))
        deleted_statuses = cur.rowcount

        conn.commit()

        return {
            "deleted": deleted_statuses > 0,
            "status_id": status_id,
            "deleted_status_rules": deleted_status_rules,
            "deleted_job_requirements": deleted_job_requirements,
            "deleted_user_statuses": deleted_user_statuses,
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def get_status_id(status_name):
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT id
            FROM master_statuses
            WHERE status_name=%s""",(status_name,))
        
        status=cur.fetchone()

        if status is None:
                return None
            
        return status["id"]
        
    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    
def import_master_status(cur,status_name,default_value,status_type):
    cur.execute("""
        INSERT INTO master_statuses
        (status_name,default_value,status_type)
        VALUES(%s,%s,%s)
        ON CONFLICT (status_name) DO NOTHING
        """,(status_name,default_value,status_type))

def import_status_csv(csv_file):
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
        "status_name",
        "default_value",
        "status_type",
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

    valid_rows = []
    errors = []

    for line_number, row in enumerate(reader, start=2):
        status_name = row["status_name"].strip()
        default_value=row["default_value"].strip()
        status_type = row["status_type"].strip().lower()

        if not status_name:
            errors.append({
                "line": line_number,
                "message": "status_nameが空です",
            })
            continue

        if not default_value:
                    errors.append({
                        "line": line_number,
                        "message": "default_valueが空です",
                    })
                    continue

        if status_type not in ("front", "back"):
            errors.append({
                "line": line_number,
                "message": "status_typeはfrontまたはbackにしてください",
            })
            continue

        valid_rows.append({
            "status_name": status_name,
            "default_value":default_value,
            "status_type": status_type,
        })

    if errors:
        return ({
            "success": False,
            "message": "CSVの内容にエラーがあります",
            "imported_count": 0,
            "errors": errors,
        })
    
    if not valid_rows:
        return ({
            "success": False,
            "message": "追加できるデータがありません",
        })

        
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        for row in valid_rows:
            import_master_status(
                cur,
                status_name=(row.get("status_name") or "").strip(),
                default_value=(row.get("default_value") or "").strip(),
                status_type=(row.get("status_type") or "").strip().lower(),
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    import_count = len(valid_rows)
    
    return ({
        "success": True,
        "message": f"{import_count}件追加しました",
        "imported_count": import_count,
        "errors": [],
    })

def get_status_id_by_name(status_name):
    conn=get_db_connection()
    cur=conn.cursor()

    cur.execute("""
        SELECT id
        FROM master_statuses
        WHERE status_name=%s""",(status_name,))

    row=cur.fetchone()

    conn.close()

    return row["id"] if row else None

