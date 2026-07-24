import sqlite3
from flask import Flask
import os
import csv
import io

from backend.queries.admin.category_queries import (
    get_category_id,
)

app=Flask(__name__)

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_NAME=os.path.join(BASE_DIR,"rpg_table.db")

def get_master_achievements():
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT master_achievements.id AS id,
                    required_category_id AS category_id,
                    master_categories.category_name AS category_name,
                    required_hours,
                    achievement_name,
                    title_name,
                    master_achievements.is_active AS is_active
            FROM master_achievements
            JOIN master_categories
            ON required_category_id=master_categories.id""")
        
        master_achievements=cur.fetchall()
        return master_achievements

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
    
def add_master_achievement(required_category_id,required_hours,achievement_name,title_name):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    try:
        cur.execute("""
            INSERT INTO master_achievements(
            required_category_id,required_hours,achievement_name,title_name)
            VALUES(?,?,?,?)
        """,(required_category_id,required_hours,achievement_name,title_name))

        conn.commit()

    except Exception:
        conn.rollback()

    finally:
        conn.close()

def edit_master_achievement(achievement_id,required_category_id,
                            required_hours,achievement_name,title_name,is_active):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    try:
        cur.execute("""
            UPDATE master_achievements
            SET required_category_id=?,
                required_hours=?,
                achievement_name=?,
                title_name=?,
                is_active=?
            WHERE id=?
            """,(required_category_id,required_hours,achievement_name,
                title_name,is_active,achievement_id))
        
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def import_achievement_csv(csv_file):
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
        "required_hours",
        "achievement_name",
        "title_name",
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
        required_hours = row["required_hours"].strip()
        achievement_name = row["achievement_name"].strip()
        title_name=row["title_name"].strip()

        if not category_name:
            errors.append({
                "line": line_number,
                "message": "category_nameが空です",
            })
            continue

        if not required_hours:
            errors.append({
                "line": line_number,
                "message": "required_hoursが空です",
            })
            continue

        if not achievement_name:
            errors.append({
                "line": line_number,
                "message": "achievement_nameが空です",
            })
            continue

        if not title_name:
            errors.append({
                "line": line_number,
                "message": "title_nameが空です",
            })
            continue

        category_id=get_category_id(category_name)

        if category_id is None:
            errors.append({
                "line":line_number,
                "message": "category_idが空です",
            })
            continue
            
        valid_rows.append({
            "category_id":category_id,
            "required_hours":required_hours,
            "achievement_name":achievement_name,
            "title_name":title_name,        
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
            import_master_achievement(
                cur,
                category_id,
                required_hours,
                achievement_name,
                title_name, 
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

def import_master_achievement(cur,category_id,required_hours,achievement_name,title_name):
    cur.execute("""
        INSERT INTO master_achievements
        (required_category_id,required_hours,achievement_name,title_name)
        VALUES(?,?,?,?)
            """,(category_id,required_hours,achievement_name,title_name))
    

    
