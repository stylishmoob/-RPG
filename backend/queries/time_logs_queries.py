from flask import Flask

from backend.db import get_db_connection

app=Flask(__name__)

def get_category_summary(period,user_id):
    conn=get_db_connection()
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
            WHERE time_logs.user_id=%s
            {and_sql} 
            AND master_categories.is_active=1
            GROUP BY master_categories.id,
                    master_categories.category_name
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
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        and_sql=check_period(period)

        cur.execute(f"""
            SELECT time_logs.category_id AS category_id,
                    master_categories.category_name AS category_name,
                    time_logs.start_time::timestamp::date AS log_date,
                    SUM(time_logs.duration_seconds) AS daily_total_seconds
            FROM time_logs
            JOIN user_categories
                ON time_logs.category_id=user_categories.id
            JOIN master_categories
                ON user_categories.master_category_id=master_categories.id
            WHERE time_logs.user_id=%s
            {and_sql}
            AND is_active=1
            GROUP BY time_logs.category_id,
                    master_categories.category_name,
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
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT 
                time_logs.category_id AS category_id,
                master_categories.category_name AS category_name,
                to_char(time_logs.start_time::timestamp,'HH24:MI:SS') AS start_time,
                to_char(time_logs.end_time::timestamp,'HH24:MI:SS') AS end_time,
                time_logs.duration_seconds AS duration_seconds
            FROM time_logs
            JOIN user_categories 
                ON time_logs.category_id=user_categories.id
            JOIN master_categories
                ON user_categories.master_category_id=master_categories.id
            WHERE time_logs.start_time::timestamp::date=CURRENT_DATE
                AND time_logs.user_id=%s
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
    conn=get_db_connection()
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
            WHERE time_logs.user_id=%s AND master_categories.is_active=1
            """,(user_id,))
        
        logs=cur.fetchall()
        return logs

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def save_time_logs(user_id,selected_category_id,start_time,end_time,duration_seconds):
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
                    INSERT INTO time_logs(user_id,category_id,start_time,end_time,duration_seconds)
                    VALUES(%s,%s,%s,%s,%s)
                    """,(user_id,selected_category_id,start_time,end_time,duration_seconds))

        conn.commit()
        
    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()    

def check_period(period):
    if period =="today":
        return "AND time_logs.start_time::timestamp::date=CURRENT_DATE"
    elif period == "7days":
        return "AND time_logs.start_time::timestamp::date >= CURRENT_DATE - INTERVAL '6 days'"
    elif period == "week":
        return "AND time_logs.start_time::timestamp::date >= (CURRENT_DATE - EXTRACT(DOW FROM CURRENT_DATE)::int * INTERVAL '1 day')::date"
    elif period == "month":
        return "AND to_char(time_logs.start_time::timestamp,'YYYY-MM') = to_char(CURRENT_DATE,'YYYY-MM')"
    elif period=="year":
        return "AND to_char(time_logs.start_time::timestamp,'YYYY') = to_char(CURRENT_DATE,'YYYY')"
    else:
        return ""
