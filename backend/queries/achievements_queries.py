from flask import Flask

from backend.db import get_db_connection

from backend.queries.time_logs_queries import(
    get_category_summary,
)

app=Flask(__name__)

def get_user_achievements(user_id):
    conn=get_db_connection()
    cur=conn.cursor()

    try:
        cur.execute("""
            SELECT  
                master_achievements.achievement_name,
                master_achievements.title_name            
            FROM user_achievements
            JOIN master_achievements
            ON user_achievements.achievement_id=master_achievements.id
            WHERE user_achievements.user_id=%s AND master_achievements.is_active=1
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
    
    conn=get_db_connection()
    cur=conn.cursor()

    category_summary=get_category_summary("all",user_id)
    category_hours={}
    for row in category_summary:
        category_hours[row["category_id"]]=(row["category_total_seconds"] or 0)/3600

    cur.execute("""
        SELECT id,required_category_id,required_hours
        FROM master_achievements
        WHERE is_active=1""")
    achievements=cur.fetchall()

    for achievement in achievements:
        total_hours=category_hours.get(achievement["required_category_id"],0)

        if total_hours >= achievement["required_hours"]:
            cur.execute("""
                INSERT INTO user_achievements(user_id,achievement_id)
                VALUES(%s,%s)
                ON CONFLICT (user_id,achievement_id) DO NOTHING
                """,(user_id,achievement["id"]))
            
            if cur.rowcount > 0:
                new_achievement_count +=1
            
    conn.commit()
    conn.close()

    return new_achievement_count
