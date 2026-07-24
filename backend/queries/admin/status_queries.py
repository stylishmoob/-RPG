import sqlite3
from flask import Flask
import os
import csv
import io

app=Flask(__name__)

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_NAME=os.path.join(BASE_DIR,"rpg_table.db")

def get_master_statuses():
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
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
        

def add_master_status(status_name,status_type):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    try:
        cur.execute("""
            INSERT INTO master_statuses
            (status_name,status_type)
            VALUES(?,?)""",(status_name,status_type))
        
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def edit_master_status(status_id,new_status_name,status_type,is_active):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    try:
        cur.execute("""
            UPDATE master_statuses
            SET status_name=?,status_type=?,is_active=?
            WHERE id=?""",(new_status_name,status_type,is_active,status_id))
        
        conn.commit()

    except Exception:
        conn.rollback()

    finally:
        conn.close()

def get_status_id(status_name):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT id
            FROM master_statuses
            WHERE name=?""",(status_name,))
        
        status_id=cur.fetchall()

        if status_id is None:
                return None
            
        return status_id
        
    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    
def import_master_status(status_name,status_type):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        INSERT INTO master_statuses
        (status_name,status_type)
        VALUES(?,?)""",(status_name,status_type))

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
        status_type = row["status_type"].strip().lower()

        if not status_name:
            errors.append({
                "line": line_number,
                "message": "status_nameが空です",
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

        
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    try:
        for row in valid_rows:
            import_master_status(
                cur,
                status_name=(row.get("status_name") or "").strip(),
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
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        SELECT id
        FROM master_statuses
        WHERE status_name=?""",(status_name,))

    row=cur.fetchone()

    conn.close()

    return row[0] if row else None

