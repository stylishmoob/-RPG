import sqlite3
from flask import Flask
import os
import csv
import io

from backend.queries.admin.category_queries import (
    get_category_id,
)
from backend.queries.admin.status_queries import (
    get_status_id,
)

app=Flask(__name__)

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_NAME=os.path.join(BASE_DIR,"rpg_table.db")

def get_master_status_rules():
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT status_up_rules.id AS id,
                    status_up_rules.category_id AS category_id,
                    master_categories.category_name AS category_name,
                    status_up_rules.status_id AS status_id,
                    master_statuses.status_name AS status_name,
                    gain_per_hours,
                    status_up_rules.is_active AS is_active
            FROM status_up_rules
            JOIN master_categories
            ON master_categories.id=status_up_rules.category_id
            JOIN master_statuses
            ON master_statuses.id=status_up_rules.status_id
            """)

        master_status_rules=cur.fetchall()

        conn.commit()
        return master_status_rules
    
    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

        
def add_status_rules(category_id,status_id,gain_per_hours):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    try:
        cur.execute("""
            INSERT INTO status_up_rules(category_id,status_id,gain_per_hours)
            VALUES(?,?,?)
            """,(category_id,status_id,gain_per_hours))
        
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def delete_status_rules(category_id,status_id):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    try:
        cur.execute("""
            DELETE FROM status_up_rules
            WHERE category_id=? AND status_id=?""",(category_id,status_id))
        
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def edit_status_rules(status_rules_id,category_id,status_id,gain_per_hours,status_rules_is_active):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    try:
        cur.execute("""
            UPDATE status_up_rules
            SET category_id = ?,
                status_id =?,
                gain_per_hours =?,
                is_active =?
            WHERE id=?
            VALUES(?,?,?,?,?)
            """,(category_id,status_id,gain_per_hours,status_rules_is_active,status_rules_id))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def import_status_rules_csv(csv_file):
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
        "category_name",
        "status_name",
        "gain_per_hours",
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
        category_name = row["category_name"].strip()
        status_name = row["status_name"].strip()
        gain_per_hours = row["gain_per_hours"].strip()

        if not category_name:
            errors.append({
                "line": line_number,
                "message": "category_nameが空です",
            })
            continue

        if not status_name:
            errors.append({
                "line": line_number,
                "message": "status_nameが空です",
            })
            continue

        if not gain_per_hours:
            errors.append({
                "line": line_number,
                "message": "gain_per_hoursが空です",
            })
            continue

        category_id=get_category_id(category_name)
        status_id=get_status_id(status_name)

        if category_id is None:
            errors.append({
                "line":line_number,
                "message": "category_idが空です",
            })
            continue

        if status_id is None:
            errors.append({
                "line":line_number,
                "message": "status_idが空です",
            })
            continue
            
        valid_rows.append({
            "category_id":category_id,
            "status_id":status_id,
            "gain_per_hours":gain_per_hours,       
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
            import_status_rules(
                cur,
                category_id,
                status_id,
                gain_per_hours,
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

def import_status_rules(cur,category_id,status_id,gain_per_hours):
    cur.execute("""
        INSERT INTO status_up_rules
        (category_id,status_id,gain_per_hours)
        VALUES(?,?,?)
            """,(category_id,status_id,gain_per_hours))