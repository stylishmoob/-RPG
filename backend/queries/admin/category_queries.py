from flask import Flask
import csv
import io

from backend.db import get_db_connection

from backend.queries.admin.common_queries import(
    insert_default_category_achievements
)

app=Flask(__name__)

def get_master_categories():
    conn=get_db_connection()
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
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            INSERT INTO master_categories(category_name)
            VALUES(%s)
            ON CONFLICT (category_name) DO NOTHING
            """,(category_name,))
        
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def edit_master_category(category_id,category_name,is_active):
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            UPDATE master_categories 
            SET category_name=%s,
                is_active=%s
            WHERE id=%s
            """,(category_name,int(is_active),category_id))
        
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def delete_master_category(category_id):
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT id
            FROM master_categories
            WHERE id=%s
            """,(category_id,))

        category = cur.fetchone()

        if category is None:
            conn.rollback()
            return {
                "deleted": False,
                "category_id": category_id,
            }

        cur.execute("""
            SELECT id
            FROM user_categories
            WHERE master_category_id=%s
            """,(category_id,))

        user_category_ids = [row["id"] for row in cur.fetchall()]

        deleted_time_logs = 0

        if user_category_ids:
            cur.execute("""
                DELETE FROM time_logs
                WHERE category_id = ANY(%s)
                """,(user_category_ids,))
            deleted_time_logs = cur.rowcount

        cur.execute("""
            DELETE FROM user_achievements
            WHERE achievement_id IN (
                SELECT id
                FROM master_achievements
                WHERE required_category_id=%s
            )
            """,(category_id,))
        deleted_user_achievements = cur.rowcount

        cur.execute("""
            DELETE FROM master_achievements
            WHERE required_category_id=%s
            """,(category_id,))
        deleted_achievements = cur.rowcount

        cur.execute("""
            DELETE FROM status_up_rules
            WHERE category_id=%s
            """,(category_id,))
        deleted_status_rules = cur.rowcount

        cur.execute("""
            DELETE FROM user_categories
            WHERE master_category_id=%s
            """,(category_id,))
        deleted_user_categories = cur.rowcount

        cur.execute("""
            DELETE FROM master_categories
            WHERE id=%s
            """,(category_id,))
        deleted_categories = cur.rowcount

        conn.commit()

        return {
            "deleted": deleted_categories > 0,
            "category_id": category_id,
            "deleted_time_logs": deleted_time_logs,
            "deleted_user_achievements": deleted_user_achievements,
            "deleted_achievements": deleted_achievements,
            "deleted_status_rules": deleted_status_rules,
            "deleted_user_categories": deleted_user_categories,
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def import_master_category(cur,category_name):
    cur.execute("""
        INSERT INTO master_categories(category_name)
        VALUES(%s)
        ON CONFLICT (category_name) DO NOTHING
        RETURNING id
        """,(category_name,))

    row=cur.fetchone()

    if row is not None:
        return row["id"]

    cur.execute("""
        SELECT id
        FROM master_categories
        WHERE category_name=%s
        """,(category_name,))

    return cur.fetchone()["id"]

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

        
    conn=get_db_connection()
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
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT id
            FROM master_categories
            WHERE category_name=%s""",(category_name,))
        
        category=cur.fetchone()

        if category is None:
            return None
        
        return category["id"]

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
