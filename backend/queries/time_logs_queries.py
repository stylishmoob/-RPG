import sqlite3
from flask import Flask
import os

app=Flask(__name__)

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_NAME=os.path.join(BASE_DIR,"rpg_table.db")

def get_category_summary(period,user_id):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    try:
        and_sql=check_period(period)
        cur.execute(f"""
            SELECT master_categories.id AS category_id,
                master_categories.category_name AS category_name,
                SUM(time_logs.duration_seconds) AS category_total_seconds     
            FROM time_logs
            JOIN user_categories
                    ON time_logs.category_id=user_categories.id
            JOIN master_categories
                ON user_categories.master_category_id=master_categories.id
            WHERE time_logs.user_id=?
            {and_sql} 
            AND master_categories.is_active=1
            GROUP BY master_categories.id
            ORDER BY category_total_seconds DESC
                    """,(user_id,))
    
        category_summary=cur.fetchall()
        return category_summary
    
    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
    

def get_daily_summary(period,user_id):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    try:
        and_sql=check_period(period)

        cur.execute(f"""
            SELECT time_logs.category_id AS category_id,
                    master_categories.category_name AS category_name,
                    DATE(time_logs.start_time) AS log_date,
                    SUM(time_logs.duration_seconds) AS daily_total_seconds
            FROM time_logs
            JOIN user_categories
                ON time_logs.category_id=user_categories.id
            JOIN master_categories
                ON user_categories.master_category_id=master_categories.id
            WHERE time_logs.user_id=?
            {and_sql}
            AND is_active=1
            GROUP BY time_logs.category_id,
                    log_date
            ORDER BY log_date,
                    daily_total_seconds DESC
                    """,(user_id,))
        
        daily_category_summary=cur.fetchall()
        return daily_category_summary

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def get_today_logs(user_id):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT 
                time_logs.category_id AS category_id,
                master_categories.category_name AS category_name,
                strftime('%H:%M:%S',time_logs.start_time,'localtime') AS start_time,
                strftime('%H:%M:%S',time_logs.end_time,'localtime') AS end_time,
                time_logs.duration_seconds AS duration_seconds
            FROM time_logs
            JOIN user_categories 
                ON time_logs.category_id=user_categories.id
            JOIN master_categories
                ON user_categories.master_category_id=master_categories.id
            WHERE DATE(time_logs.start_time,'localtime')=DATE('now','localtime')
                AND time_logs.user_id=?
                AND master_categories.is_active=1
            ORDER BY time_logs.start_time
            """,(user_id,))
        
        today_logs=cur.fetchall()
        return today_logs

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def get_time_logs(user_id):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT master_categories.category_name,
                    time_logs.start_time,
                    time_logs.end_time,
                    time_logs.duration_seconds
            FROM time_logs
            JOIN user_categories
            ON time_logs.category_id=user_categories.id
            JOIN master_categories
            ON user_categories.master_category_id=master_categories.id
            WHERE time_logs.user_id=? AND master_categories.is_active=1
            """,(user_id,))
        
        logs=cur.fetchall()
        return logs

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def save_time_logs(cur,user_id,selected_category_id,start_time,end_time,duration_seconds):
    cur.execute("""
                INSERT INTO time_logs(user_id,category_id,start_time,end_time,duration_seconds)
                VALUES(?,?,?,?,?)
                """,(user_id,selected_category_id,start_time,end_time,duration_seconds))    

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