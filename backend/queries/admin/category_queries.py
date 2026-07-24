import sqlite3
from flask import Flask
import os
import csv
import io

from backend.queries.admin.common_queries import(
    insert_default_category_achievements
)

app=Flask(__name__)

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_NAME=os.path.join(BASE_DIR,"rpg_table.db")

def get_master_categories():
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT * FROM master_categories""")
        
        master_categories=cur.fetchall()
        return master_categories

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
        

def add_master_category(category_name):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    try:
        cur.execute("""
            INSERT OR IGNORE INTO master_categories(category_name)
            VALUES(?)
            """,(category_name,))
        
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def edit_master_category(category_id,category_name,category_is_active):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    try:
        cur.execute("""
            UPDATE master_categories SET category_name=? is_active=?
            WHERE id=?
            """,(category_name,category_is_active,category_id))
        
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def import_master_category(cur,category_name):
    cur.execute("""
        INSERT OR IGNORE INTO master_categories(category_name)
        VALUES(?)
        """,(category_name,))
    
    return cur.lastrowid

def import_category_csv(csv_file):
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

        if not category_name:
            errors.append({
                "line": line_number,
                "message": "status_nameが空です",
            })
            continue

        valid_rows.append({
            "category_name": category_name,
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
            category_name=(row.get("category_name") or "").strip()

            category_id=import_master_category(
                cur,
                category_name,
            )

            insert_default_category_achievements(
                cur,
                category_id,
                category_name
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

def get_category_id(category_name):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT id
            FROM master_categories
            WHERE name=?""",(category_name,))
        
        category_id=cur.fetchone()

        if category_id is None:
            return None
        
        return category_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()