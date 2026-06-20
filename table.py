import sqlite3
import os

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_NAME=os.path.join(BASE_DIR,"rpg_table.db")

def init_db():
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS time_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id TEXT,
        start_time TEXT,
        end_time TEXT,
        duration_seconds INTEGER   )""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT)""")
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_front_status(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        STR INTEGER DEFAULT 10,
        INT INTEGER DEFAULT 10,
        SKL INTEGER DEFAULT 10,
        CRE INTEGER DEFAULT 10,
        WIL INTEGER DEFAULT 10)""")
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS status_up_rules(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        status_name TEXT,
        gain_per_hours REAL )""")
    
    conn.commit()
    conn.close()

def add_user_id():
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM user_front_status
        """)
    
    count=cur.fetchone()[0]
    if count==0:
        cur.execute("""
            INSERT INTO user_front_status DEFAULT VALUES
            """)
    
    conn.commit()
    conn.close()

def init_category_rules():
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM status_up_rules
        """)
    count=cur.fetchone()[0]

    if count==0:
        cur.execute("""
            INSERT INTO status_up_rules
            (category_id,status_name,gain_per_hours) 
            VALUES(1,'INT',100)""")
    
        cur.execute("""
            INSERT INTO status_up_rules
            (category_id,status_name,gain_per_hours)
            VALUES(2,'STR',100)""")
    
    conn.commit()
    conn.close()


init_db()
init_category_rules()
add_user_id()