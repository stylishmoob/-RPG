import sqlite3
from flask import Flask
import os
import io
import csv

app=Flask(__name__)

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_NAME=os.path.join(BASE_DIR,"rpg_table.db")


def get_time_logs(user_id):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        SELECT master_categories.category_name,
                time_logs.start_time,
                time_logs.end_time,
                time_logs.duration_seconds
        FROM time_logs
        JOIN categories
        ON time_logs.category_id=categories.id
        JOIN master_categories
        ON categories.master_category_id=master_categories.id
        WHERE time_logs.user_id=? AND master_categories.is_active=1
         """,(user_id,))
    
    logs=cur.fetchall()

    conn.close()
    return logs

def get_user_categories(user_id):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    cur.execute("""
        SELECT categories.id AS category_id,
               category_name 
        FROM categories
        JOIN master_categories
        ON categories.master_category_id=master_categories.id
        WHERE user_id=? AND master_categories.is_active=1""",(user_id,))
    
    user_categories=cur.fetchall()

    conn.close()
    return user_categories

def get_user_status(user_id):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    cur.execute("""
        SELECT  users_status.id AS status_id, 
                status_name,
                status_value,
                status_type
        FROM users_status
        JOIN users
        ON users.id=users_status.user_id
        JOIN statuses
        ON statuses.id=users_status.status_id
        WHERE user_id=?
        ORDER BY statuses.id""",(user_id,))
    
    user_status_row=cur.fetchall()

    conn.close()
    return user_status_row

def get_user_by_id(user_id):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()
    
    cur.execute("""
        SELECT id,
                user_name,
                password_hash,
                user_level,
                is_admin
        FROM users
        WHERE id=?""",(user_id,))
    
    user=cur.fetchone()

    conn.close()
    return user

def get_user_by_name(user_name):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()
    
    cur.execute("""
        SELECT id,
                user_name,
                password_hash,
                user_level,
                is_admin
        FROM users
        WHERE user_name=?""",(user_name,))
    
    user=cur.fetchone()

    conn.close()
    return user

def get_status_up_rules():
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        SELECT master_categories.id,
                master_categories.category_name,
                statuses.status_name,
                statuses.status_type,
                status_up_rules.gain_per_hours 
        FROM status_up_rules
        JOIN master_categories
        ON status_up_rules.category_id=master_categories.id
        JOIN statuses
        ON status_up_rules.status_id=statuses.id
        WHERE master_categories.is_active=1 """)
    
    status_up_rules=cur.fetchall()
    
    conn.close()
    return status_up_rules

def get_user_achievements(user_id):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    cur.execute("""
        SELECT  
            achievements.achievement_name,
            achievements.title_name            
        FROM user_achievements
        JOIN achievements
        ON user_achievements.achievement_id=achievements.id
        WHERE user_achievements.user_id=? AND achievements.is_active=1
        ORDER BY achievements.id ASC  """,(user_id,))
    
    user_achievements=cur.fetchall()

    conn.close()
    return user_achievements

def get_user_jobs(user_id):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        SELECT  job_id,
                job_name
        FROM users_job
        JOIN jobs_requirement
        ON users_job.job_id=jobs_requirement.id
        WHERE users_job.user_id=? 
        AND jobs_requirement.is_active=1
        AND users_job.is_active=1
        """,(user_id,))
    
    user_job=cur.fetchone() 
    conn.close()
    return user_job

def save_time_logs(user_id,selected_category_id,start_time,end_time,duration_seconds):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()
    
    cur.execute("""
                INSERT INTO time_logs(user_id,category_id,start_time,end_time,duration_seconds)
                VALUES(?,?,?,?,?)
                """,(user_id,selected_category_id,start_time,end_time,duration_seconds))
    
    conn.commit()
    conn.close()

def get_user_master_categories():
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    cur.execute("""
        SELECT id ,
                category_name
        FROM master_categories
        WHERE is_active=1""")
    
    user_master_categories=cur.fetchall()

    conn.close()
    return user_master_categories

def add_user_category(user_id,master_category_id):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        INSERT OR IGNORE INTO categories(user_id,master_category_id)
        VALUES (?,?)""",(user_id,master_category_id)) 
    
    conn.commit()
    conn.close()

def edit_user_category(user_id,master_category_id,category_id):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        UPDATE categories SET master_category_id=?
        WHERE id =? AND user_id=?
        """,(master_category_id,category_id,user_id))
    
    conn.commit()
    conn.close()

def delete_user_category(user_id,category_id):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        DELETE FROM categories
        WHERE id =? AND user_id=?""",(category_id,user_id))

    cur.execute("""
        DELETE FROM time_logs
        WHERE category_id=? AND user_id=?""",(category_id,user_id))
    
    conn.commit()
    conn.close()

def get_today_logs(user_id):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    cur.execute("""
        SELECT 
            time_logs.category_id AS category_id,
            master_categories.category_name AS category_name,
            strftime('%H:%M:%S',time_logs.start_time,'localtime') AS start_time,
            strftime('%H:%M:%S',time_logs.end_time,'localtime') AS end_time,
            time_logs.duration_seconds AS duration_seconds
        FROM time_logs
        JOIN categories 
            ON time_logs.category_id=categories.id
        JOIN master_categories
            ON categories.master_category_id=master_categories.id
        WHERE DATE(time_logs.start_time,'localtime')=DATE('now','localtime')
            AND time_logs.user_id=?
            AND master_categories.is_active=1
        ORDER BY time_logs.start_time
        """,(user_id,))
    
    today_logs=cur.fetchall()
    conn.close()

    return today_logs

def get_category_summary(period,user_id):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    and_sql=check_period(period)
    cur.execute(f"""
        SELECT master_categories.id AS category_id,
               master_categories.category_name AS category_name,
               SUM(time_logs.duration_seconds) AS category_total_seconds     
        FROM time_logs
        JOIN categories
                ON time_logs.category_id=categories.id
        JOIN master_categories
            ON categories.master_category_id=master_categories.id
        WHERE time_logs.user_id=?
        {and_sql} 
        AND master_categories.is_active=1
        GROUP BY master_categories.id
        ORDER BY category_total_seconds DESC
                """,(user_id,))
    
    category_summary=cur.fetchall()
    conn.close()
    return category_summary

def check_category_achievement(user_id):
    new_achievement_count=0
    
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    category_summary=get_category_summary("all",user_id)
    category_hours={}
    for category_id,category_name,total_seconds in category_summary:
        category_hours[category_id]=total_seconds/3600

        cur.execute("""
            SELECT id,required_category_id,required_hours
            FROM achievements
            WHERE is_active=1""")
        achievements=cur.fetchall()

    for achievement_id,required_category_id,required_hours in achievements:
        total_hours=category_hours.get(required_category_id,0)

        if total_hours >=required_hours:
            before=conn.total_changes

            cur.execute("""
                INSERT OR IGNORE INTO user_achievements(user_id,achievement_id)
                VALUES(?,?)
                """,(user_id,achievement_id))
            
            after=conn.total_changes

            if after>before:
                new_achievement_count +=1
            
    conn.commit()
    conn.close()

    return new_achievement_count
        
#多分SELECT JOIN　であたらしい配列作れば行けそう

def get_daily_summary(period,user_id):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    and_sql=check_period(period)

    cur.execute(f"""
        SELECT time_logs.category_id AS category_id,
                master_categories.category_name AS category_name,
                DATE(time_logs.start_time) AS log_date,
                SUM(time_logs.duration_seconds) AS daily_total_seconds
        FROM time_logs
        JOIN categories
            ON time_logs.category_id=categories.id
        JOIN master_categories
            ON categories.master_category_id=master_categories.id
        WHERE time_logs.user_id=?
        {and_sql}
        AND is_active=1
        GROUP BY time_logs.category_id,
                log_date
        ORDER BY log_date,
                daily_total_seconds DESC
                """,(user_id,))
    
    daily_category_summary=cur.fetchall()

    conn.close()

    return daily_category_summary

def check_period(period):
    if period =="today":
        return "AND DATE(start_time,'localtime')=DATE('now','localtime')"
    elif period == "7days":
        return "AND DATE(start_time,'localtime') >= DATE('now','localtime','-6 days')"
    elif period == "week":
        return "AND DATE(start_time,'localtime') >= DATE('now','localtime','-'||strftime('%w','now','localtime') || ' days')"
    elif period == "month":
        return "AND strftime('%Y-%m',start_time,'localtime') =strftime('%Y-%m','now','localtime')"
    elif period=="year":
        return "AND strftime('%Y',start_time,'localtime')=strftime('%Y','now','localtime')"
    else:
        return ""
       

def status_cir(category_id,duration_seconds,user_id):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        SELECT sur.status_id,
                sur.gain_per_hours
        FROM categories c
        JOIN status_up_rules sur
            ON c.master_category_id = sur.category_id
        WHERE c.id=?""",(category_id,))

    rules=cur.fetchall()

    for status_id,gain_per_hours in rules:
        gain=duration_seconds / 3600 * gain_per_hours

        cur.execute("""
            UPDATE users_status
            SET status_value=status_value+?
            WHERE status_id=? AND user_id=?""",
            (gain,status_id,user_id))
    #経験値効率設定変更可
    exp=(duration_seconds / 3600 )*(360) 

    cur.execute("""
        UPDATE users
        SET user_level=user_level+?
        WHERE users.id=?""",(exp,user_id))
        
    conn.commit()
    conn.close()

def check_user_job(user_id):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        SELECT status_id,
                status_value
        FROM users_status
        WHERE user_id=?
        """,(user_id,))
    
    user_status=dict(cur.fetchall())

    cur.execute("""
        SELECT id,
               job_name,
                required_status_id_1,
                required_status1_value,
                required_status_id_2,
                required_status2_value
            FROM jobs_requirement
            WHERE is_active=1  
        """)
    jobs=cur.fetchall()

#思いつかない
    for job_id,job_name,stat1,value1,stat2,value2 in jobs:

        ok1=user_status.get(stat1,0) >= value1

        if stat2 is None:
            ok2=True
        else:
            ok2=user_status.get(stat2,0) >= value2

        if ok1 and ok2:
            cur.execute("""
                    SELECT 1
                    FROM users_job
                    WHERE user_id=?
                    AND job_id=?
                        """,(user_id,job_id))
            
            already_has_job=cur.fetchone()

            if already_has_job is None:
                cur.execute("""
                    UPDATE users_job SET is_active=0
                    WHERE user_id=?""",(user_id,))
                
                cur.execute("""INSERT INTO users_job(user_id,job_id,is_active)
                            VALUES(?,?,1)""",(user_id,job_id))
           
    conn.commit()
    conn.close()

def get_master_categories():
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    cur.execute("""
        SELECT * FROM master_categories""")
    
    master_categories=cur.fetchall()

    conn.close()
    return master_categories

def add_master_category(category_name):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        INSERT OR IGNORE INTO master_categories(category_name)
        VALUES(?)
        """,(category_name,))
    
    conn.commit()
    conn.close()

def import_master_category(cur,category_name):
    cur.execute("""
        INSERT OR IGNORE INTO master_categories(category_name)
        VALUES(?)
        """,(category_name,))
    
    return cur.lastrowid


def edit_master_category(category_id,category_name,category_is_active):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()
    
    cur.execute("""
        UPDATE master_categories SET category_name=? category_is_active=?
        WHERE id=?
        """,(category_name,category_is_active,category_id))
    
    conn.commit()
    conn.close()

def toggle_master_category(master_category_id):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        UPDATE master_categories 
        SET is_active = 
            CASE
                WHEN is_active=1 THEN 0
                ELSE 1
            END
        WHERE id=?
        """,(master_category_id,))
    
    conn.commit()
    conn.close()

def get_master_status_rules():
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    cur.execute("""
        SELECT status_up_rules.id AS id,
                status_up_rules.category_id AS category_id,
                master_categories.category_name AS category_name,
                status_up_rules.status_id AS status_id,
                statuses.status_name AS status_name,
                gain_per_hours
        FROM status_up_rules
        JOIN master_categories
        ON master_categories.id=status_up_rules.category_id
        JOIN statuses
        ON statuses.id=status_up_rules.status_id
          """)

    master_status_rules=cur.fetchall()

    conn.commit()
    conn.close()

    return master_status_rules

def add_status_rules(category_id,status_id,gain_per_hours):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        INSERT INTO status_up_rules(category_id,status_id,gain_per_hours)
        VALUES(?,?,?)
        """,(category_id,status_id,gain_per_hours))
    
    conn.commit()
    conn.close()
    
def delete_status_rules(category_id,status_id):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        DELETE FROM status_up_rules
        WHERE category_id=? AND status_id=?""",(category_id,status_id))
    
    conn.commit()
    conn.close()

def get_master_achievements():
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    cur.execute("""
        SELECT achievements.id AS id,
                required_category_id AS category_id,
                master_categories.category_name AS category_name,
                required_hours,
                achievement_name,
                title_name,
                achievements.is_active AS is_active
        FROM achievements
        JOIN master_categories
        ON required_category_id=master_categories.id""")
    
    master_achievements=cur.fetchall()

    conn.close()
    return master_achievements

def add_master_achievement(required_category_id,required_hours,achievement_name,title_name):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        INSERT INTO achievements(
        required_category_id,required_hours,achievement_name,title_name)
        VALUES(?,?,?,?)
    """,(required_category_id,required_hours,achievement_name,title_name))

    conn.commit()
    conn.close()

def toggle_master_achievement(achievement_id):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
           UPDATE achievements
        SET is_active=
            CASE
                WHEN is_active= 1 THEN 0
                ELSE 1
            END
        WHERE id=?
        """,(achievement_id,))
    
    conn.commit()
    conn.close()

def edit_master_achievement(achievement_id,required_category_id,
                            required_hours,achievement_name,title_name,is_active):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        UPDATE achievements
        SET required_category_id=?,
            required_hours=?,
            achievement_name=?,
            title_name=?,
            is_active=?
        WHERE id=?
        """,(required_category_id,required_hours,achievement_name,
             title_name,is_active,achievement_id))
    
    conn.commit()
    conn.close()

def get_master_statuses():
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    cur.execute("""
        SELECT * FROM statuses""")
    
    master_statuses=cur.fetchall()

    conn.close()
    return master_statuses

def add_master_status(status_name,status_type):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        INSERT INTO statuses
        (status_name,status_type)
        VALUES(?,?)""",(status_name,status_type))
    
    conn.commit()
    conn.close()

def import_master_status(status_name,status_type):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        INSERT INTO statuses
        (status_name,status_type)
        VALUES(?,?)""",(status_name,status_type))

def edit_master_status(status_id,new_status_name,status_type,is_active):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        UPDATE statuses
        SET status_name=?,status_type=?,is_active=?
        WHERE id=?""",(new_status_name,status_type,is_active,status_id))
    
    conn.commit()
    conn.close()

def toggle_master_status(status_id):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        UPDATE statuses
        SET is_active=
            CASE
                WHEN is_active=1 THEN 0
                ELSE 1
            END
        WHERE id=?
        """,(status_id,))
    
    conn.commit()
    conn.close()

def get_master_jobs_requirement():
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        SELECT jobs_requirement.id,
                jobs_requirement.job_name,
                s1.status_name,
                jobs_requirement.required_status1_value,
                s2.status_name,
                jobs_requirement.required_status2_value,
                jobs_requirement.is_active,
                jobs_requirement.is_default
        FROM jobs_requirement
        LEFT JOIN statuses AS s1
            ON jobs_requirement.required_status_id_1=s1.id
        LEFT JOIN statuses AS s2
            ON jobs_requirement.required_status_id_2=s2.id
             """)
    
    master_jobs=cur.fetchall()
    conn.close()

    return master_jobs

def add_master_job(job_name,status_id_1,required_status1_value,status_id_2,required_status2_value):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        INSERT INTO jobs_requirement(job_name,required_status_id_1,required_status1_value,
                required_status_id_2,required_status2_value)
                VALUES(?,?,?,?,?)""",(job_name,status_id_1,required_status1_value,
                                      status_id_2,required_status2_value))
    
    conn.commit()
    conn.close()

def toggle_master_job(job_id):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        UPDATE jobs_requirement 
        SET is_active=
            CASE 
                WHEN is_acitive=0 THEN 0
                ELSE 1
            END
        WHERE id=?              
        """,(job_id,))
    
    conn.commit()
    conn.close()

def get_users():
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        SELECT id,user_name,user_level,is_admin
        FROM users
                """)
    
    users=cur.fetchall()

    conn.close()
    return users

def create_user(user_name):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        INSERT INTO users(user_name)
        VALUES(?)""",(user_name,))
    
    user_id=cur.lastrowid

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
            FROM statuses
            WHERE status_name=? 
            AND is_active=1""",(status_name,))
        
        status_id=cur.fetchone()[0]

        cur.execute("""
            INSERT OR IGNORE INTO users_status
            (user_id,status_id,status_value)
            VALUES(?,?,?)""",(user_id,status_id,status_value))
          
    cur.execute("""
        INSERT INTO users_job(user_id,job_id,is_active)
        SELECT ?,id,1
        FROM jobs_requirement
        WHERE is_default=1
        """,(user_id,))
    
    conn.commit()
    conn.close()

def get_category_id(category_name):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    cur.execute("""
        SELECT id
        FROM master_categories
        WHERE name=?""",(category_name,))
    
    category_id=cur.fetchall()

    conn.close()

    if category_id is None:
        return None
    
    return category_id

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
            import_master_status(
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
        INSERT INTO achievements
        (required_category_id,required_hours,achievement_name,title_name)
        VALUES(?,?,?,?)
            """,(category_id,required_hours,achievement_name,title_name))
    

    
def insert_default_category_achievements(cur,category_id,category_name):
    DEFAULT_CATEGORY_ACHIEVEMENTS = [
    {"required_hours": 1,"title_name": "入門者",},
    {"required_hours": 10,"title_name": "見習い",},
    {"required_hours": 50,"title_name": "初級者",},
    {"required_hours": 100,"title_name": "熟練者",},
    {"required_hours": 500,"title_name": "達人",},
    {"required_hours": 1000,"title_name": "名人",},
    {"required_hours": 2000,"title_name": "極めし者",},
    {"required_hours": 3000,"title_name": "伝説",},
    ]

    for achievement in DEFAULT_CATEGORY_ACHIEVEMENTS:
        cur.execute("""
            INSERT INTO achievements (
                required_category_id,
                required_hours,
                achievement_name,
                title_name
            )
            VALUES(?,?,?,?)
            """,
            (  
                category_id,
                achievement["required_hours"],
                f"{category_name}{achievement['required_hours']}時間達成!",
                f"{category_name}{achievement['title_name']}",
            ),
        )
    