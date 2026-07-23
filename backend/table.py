import sqlite3
import os
from werkzeug.security import generate_password_hash

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_NAME=os.path.join(BASE_DIR,"rpg_table.db")

def init_db():
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
            CREATE TABLE IF NOT EXISTS master_categories(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE,
            is_active INTEGER NOT NULL DEFAULT 1 )""")

    cur.execute("""
            CREATE TABLE IF NOT EXISTS master_statuses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status_name TEXT NOT NULL UNIQUE,
            status_type TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1
            )""")

    cur.execute("""
            CREATE TABLE IF NOT EXISTS master_achievements(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            required_category_id INTEGER NOT NULL,
            required_hours INTEGER NOT NULL,
            achievement_name TEXT NOT NULL,
            title_name TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
    
            FOREIGN KEY(required_category_id) REFERENCES master_categories(id)
            )""")

    cur.execute("""
            CREATE TABLE IF NOT EXISTS master_jobs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT NOT NULL UNIQUE,
            is_active INTEGER NOT NULL DEFAULT 1,
            is_default INTEGER DEFAULT 0
            )""")

    cur.execute("""
            CREATE TABLE IF NOT EXISTS status_up_rules(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            status_id INTEGER NOT NULL,
            gain_per_hours REAL,
            is_active INTEGER NOT NULL DEFAULT 1,
    
            UNIQUE(category_id,status_id),
             
            FOREIGN KEY(category_id) REFERENCES master_categories(id),
            FOREIGN KEY(status_id) REFERENCES master_statuses(id) 
            )""")

    cur.execute("""
            CREATE TABLE IF NOT EXISTS job_requirements(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            required_status_id INTEGER NOT NULL,
            required_status_value INTEGER NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
    
            FOREIGN KEY(job_id) REFERENCES master_jobs(id),
            FOREIGN KEY(required_status_id) REFERENCES master_statuses(id),
    
            UNIQUE(job_id, required_status_id)
            )""")

    cur.execute("""
            CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            current_job_id INTEGER NOT NULL,
            user_level REAL DEFAULT 1,
            is_active INTEGER NOT NULL DEFAULT 1,
            is_admin INTEGER DEFAULT 0,
    
            FOREIGN KEY (current_job_id) REFERENCES master_jobs(id)
                    )""")

    cur.execute("""
            CREATE TABLE IF NOT EXISTS user_categories(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            master_category_id INTEGER NOT NULL,
            UNIQUE(user_id,master_category_id),
            
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (master_category_id) REFERENCES master_categories(id))""")

    cur.execute("""
            CREATE TABLE IF NOT EXISTS user_statuses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            status_id INTEGER NOT NULL,
            status_value REAL DEFAULT 10,
            UNIQUE(user_id,status_id),
    
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(status_id) REFERENCES master_statuses(id) 
                    )
            """)

    cur.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            achievement_id INTEGER NOT NULL,
            UNIQUE(user_id,achievement_id),
    
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(achievement_id) REFERENCES master_achievements(id)
            )""")

    cur.execute("""
            CREATE TABLE IF NOT EXISTS user_jobs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            UNIQUE(user_id,job_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(job_id) REFERENCES master_jobs(id)
            )
            """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS time_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        start_time TEXT,
        end_time TEXT,
        duration_seconds INTEGER,
          
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (category_id) REFERENCES master_categories(id)  )""")

    conn.commit()
    conn.close()


def add_master_user_id():
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    user_name="administrator"
    password="1111"
    password_hash=generate_password_hash(password)

    try:
        cur.execute("""
            SELECT id
            FROM master_jobs
            WHERE is_default =1""")

        job_row=cur.fetchone()

        if job_row is None:
            raise ValueError("デフォルトジョブが存在しません")

        default_job_id = job_row[0]

        cur.execute("""
            INSERT OR IGNORE INTO users 
            (user_name,
            password_hash,
            current_job_id,
            user_level,
            is_admin
            )
            VALUES(?,?,?,100,1)
            """,(user_name,password_hash,default_job_id))

        cur.execute("""
                SELECT id
                FROM users
                WHERE is_admin=1
                """)
        
        user_id = cur.fetchone()[0]
        
        statuses = {
        "HP": 100,
        "MP": 30,
        "STR": 10,
        "INT": 10,
        "SKL": 10,
        "CRE": 10,
        "WIL": 10
    }
        for status_name,status_value in statuses.items():
            cur.execute("""
                SELECT id
                FROM master_statuses
                WHERE status_name=?
                """,(status_name,))
            
            status_row=cur.fetchone()

            if status_row is None:
                raise ValueError(
                    f"ステータスが存在しません:{status_name}"
                )

            status_id =status_row[0]

            cur.execute("""
                INSERT OR IGNORE INTO user_statuses
                (user_id,
                status_id,
                status_value
                )
                VALUES(?,?,?)""",(user_id,
                                  status_id,
                                  status_value,))
            
        cur.execute("""
            INSERT INTO user_jobs(
                user_id,
                job_id)
            VALUES(?,?)
            """,(user_id,default_job_id,))
        
            
        conn.commit()

    except:
        conn.rollback()
        raise
    
    finally:
        conn.close()

def init_statuses():
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    init_statuses=[("HP","front"),("MP","front"),("STR","front"),("INT","front"),
                   ("SKL","front"),("CRE","front"),
                   ("WIL","front")]
    
    for status_name,status_type in init_statuses:
        cur.execute("""
            INSERT OR IGNORE INTO master_statuses
            (status_name,status_type)
            VALUES(?,?)
        """,(status_name,status_type))

    conn.commit()
    conn.close()

def init_jobs():
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        SELECT id
        FROM master_jobs
        WHERE job_name=?""",("放浪者",))

    row=cur.fetchone()

    if row is None:
        cur.execute("""
            INSERT INTO master_jobs
            (
            job_name,
            is_default
            )
            VALUES(?,?)
            """,("放浪者",1))
    
    conn.commit()
    conn.close()

init_db()
init_statuses()
init_jobs()
add_master_user_id()
