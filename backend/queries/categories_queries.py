import sqlite3
from flask import Flask
import os

app=Flask(__name__)

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_NAME=os.path.join(BASE_DIR,"rpg_table.db")

def get_user_categories(user_id):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    cur.execute("""
        SELECT user_categories.id AS category_id,
               master_categories.category_name AS category_name
        FROM user_categories
        JOIN master_categories
        ON user_categories.master_category_id=master_categories.id
        WHERE user_id=? 
        AND master_categories.is_active=1
        """,(user_id,)
    )
    user_categories=cur.fetchall()

    conn.close()

    return user_categories

def get_user_master_categories():
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT id ,
                    category_name
            FROM master_categories
            WHERE is_active=1""")
    
        user_master_categories=cur.fetchall()
        return user_master_categories

    finally:
        conn.close()
    

def delete_user_category(user_id,category_id):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    try:
        cur.execute("""
            DELETE FROM user_categories
            WHERE id =? 
            AND user_id=?
            """,(category_id,user_id))

        cur.execute("""
            DELETE FROM time_logs
            WHERE category_id=? 
            AND user_id=?
            """,(category_id,user_id))
        
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def add_user_category(user_id,master_category_id):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    try:
        cur.execute("""
            INSERT OR IGNORE INTO user_categories
            (user_id,master_category_id)
            VALUES (?,?)
            """,(user_id,master_category_id)) 
    
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def edit_user_category(user_id,master_category_id,category_id):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    try:
        cur.execute("""
            UPDATE user_categories 
            SET master_category_id=?
            WHERE id =? 
            AND user_id=?
            """,(master_category_id,category_id,user_id))
    
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()