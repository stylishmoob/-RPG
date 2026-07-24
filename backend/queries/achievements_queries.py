import sqlite3
from flask import Flask
import os

from backend.queries.time_logs_queries import(
    get_category_summary,
)

app=Flask(__name__)

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_NAME=os.path.join(BASE_DIR,"rpg_table.db")

def get_user_achievements(user_id):
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT  
                master_achievements.achievement_name,
                master_achievements.title_name            
            FROM user_achievements
            JOIN master_achievements
            ON user_achievements.achievement_id=master_achievements.id
            WHERE user_achievements.user_id=? AND master_achievements.is_active=1
            ORDER BY master_achievements.id ASC  """,(user_id,))
        
        user_achievements=cur.fetchall()
        return user_achievements

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

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
            FROM master_achievements
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