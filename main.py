import sqlite3
from flask import Flask,render_template,request,redirect,url_for
import os,math

app=Flask(__name__)

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_NAME=os.path.join(BASE_DIR,"rpg_table.db")

def get_time_logs():
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        SELECT * FROM time_logs """)
    
    logs=cur.fetchall()

    conn.close()
    return logs

def get_categories():
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        SELECT * FROM categories""")
    
    categories=cur.fetchall()

    conn.close()
    return categories

def get_user_status():
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        SELECT STR,INT,SKL,CRE,WIL FROM user_front_status
        WHERE user_id=1""")
    
    front_status=cur.fetchone()

    conn.close()
    return front_status

def add_category_name(category_name):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        INSERT OR IGNORE INTO categories(category_name)
        VALUES (?)""",(category_name,))
    
    conn.commit()
    conn.close()

def edit_category_name(category_id,new_name):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        UPDATE categories SET category_name=?
        WHERE id =?
        """,(new_name,category_id))
    
    conn.commit()
    conn.close()

def delete_category_name(category_id):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        DELETE FROM categories
        WHERE id =?""",(category_id,))

    cur.execute("""
        DELETE FROM time_logs
        WHERE category_id=?""",(category_id,))
    
    conn.commit()
    conn.close()

def get_today_logs():
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        SELECT 
            time_logs.category_id,
            categories.category_name,
            strftime('%H:%M:%S',time_logs.start_time),
            strftime('%H:%M:%S',time_logs.end_time),
            time_logs.duration_seconds
        FROM time_logs
        JOIN categories 
            ON time_logs.category_id=categories.id
        WHERE DATE(time_logs.start_time,'localtime')=DATE('now','localtime')
        ORDER BY time_logs.start_time
        """)
    
    today_logs=cur.fetchall()
    conn.close()

    return today_logs

def get_category_logs():
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()
 
    cur.execute("""
        SELECT time_logs.category_id
        categories""")

def get_category_summary(period):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    where_sql=check_period(period)
    cur.execute(f"""
        SELECT time_logs.category_id,
               categories.category_name,
               SUM(time_logs.duration_seconds)      
        FROM time_logs
        JOIN categories
                ON time_logs.category_id=categories.id
        {where_sql}
        GROUP BY time_logs.category_id
        ORDER BY SUM(time_logs.duration_seconds) DESC
                """)
    
    category_summary=cur.fetchall()
    conn.close()
    return category_summary

def get_daily_summary(period):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    where_sql=check_period(period)
    cur.execute(f"""
        SELECT time_logs.category_id,
                categories.category_name,
                DATE(time_logs.start_time) AS log_date,
                SUM(time_logs.duration_seconds) AS total_seconds
        FROM time_logs
        JOIN categories
            ON time_logs.category_id=categories.id
        {where_sql}
        GROUP BY time_logs.category_id,
                log_date,
                categories.category_name
        ORDER BY log_date,
                total_seconds
                """)
    daily_category_summary=cur.fetchall()

    conn.close()

    return daily_category_summary

def check_period(period):
    if period =="today":
        where="WHERE DATE(start_time)=DATE('now','localtime')"
    elif period == "week":
        where="WHERE DATE(start_time)=DATE('now','-6 days','localtime')"
    elif period == "month":
        where="WHERE strftime('%Y-%m',start_time) =strftime('%Y-%m','now','localtime')"
    elif period=="year":
        where="WHERE strftime('%Y',start_time)=strftime('%Y','now','localtime')"
    else:
        where=""
    
    return where   

def status_cir(category_id,duration_seconds):
    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()

    cur.execute("""
        SELECT status_name,gain_per_hours
        FROM status_up_rules
        WHERE category_id=?
        """,(category_id,))

    rules=cur.fetchall()

    for status_name,gain_per_hours in rules:
        gain=duration_seconds / 3600 * gain_per_hours

        cur.execute(f"""
            UPDATE user_front_status
            SET {status_name}={status_name}+?
            WHERE user_id=1""",
            (gain,))
        
    conn.commit()
    conn.close()




@app.route("/",methods=["GET","POST"])
def home():
    logs=get_time_logs()
    categories=get_categories()
    today_logs=get_today_logs()
    front_status=get_user_status()

    return render_template("home.html",logs=logs,categories=categories,today_logs=today_logs,
                           front_status=front_status)

@app.route("/save_action",methods=["GET","POST"])
def save_action():
    if request.method=="POST":
        action=request.form["action"]
        if action=="save_seconds":

            selected_category_id=(request.form["category_id"])
            start_time=request.form["start_time"]
            end_time=request.form["end_time"]
            duration_seconds=int(request.form["duration_seconds"])

            conn=sqlite3.connect(DB_NAME)
            cur=conn.cursor()
    
            cur.execute("""
                INSERT INTO time_logs(category_id,start_time,end_time,duration_seconds)
                VALUES(?,?,?,?)""",(selected_category_id,start_time,end_time,duration_seconds))
    
            conn.commit()
            conn.close()

            status_cir(selected_category_id,duration_seconds)


    return redirect("/")

@app.route("/category",methods=["GET","POST"])
def category():
    if request.method=="POST":
        action=request.form["action"]

        if action == "add_category_name":
            category_name=request.form["category_name"]
            add_category_name(category_name)

        elif action == "edit_category_name":
            new_name=request.form["new_name"]
            category_id=request.form["category_id"]
            edit_category_name(category_id,new_name)

        elif action == "delete_category_name":
            category_id=request.form["category_id"]
            delete_category_name(category_id)

        return redirect(url_for("category"))
    
    categories=get_categories()

    return render_template("category.html",categories=categories)

@app.route("/history",methods=["GET","POST"])
def history():

    ctx1_period=request.args.get("ctx1_period","all")
    ctx1_unit=request.args.get("ctx1_unit","minutes")
    ctx2_period=request.args.get("ctx2_period","all")
    ctx2_unit=request.args.get("ctx2_unit","minutes")

    category_summary=get_category_summary(ctx1_period)
    new_category_summary=[]

    for row in category_summary:
        if ctx1_unit=="seconds":
            value=row[2]
        elif ctx1_unit=="minutes":
            value=round(row[2]/60,2)
        else:
            value=round(row[2]/3600,2)

        new_category_summary.append((row[0],row[1],value))

    category_summary=new_category_summary

    daily_category_summary=get_daily_summary(ctx2_period)
    new_daily_category_summary=[]

    for row in daily_category_summary:
        if ctx2_unit=="seconds":
            value=row[3]
        elif ctx2_unit=="minutes":
            value=round(row[3]/60,2)
        else:
            value=round(row[3]/3600,2)

        new_daily_category_summary.append((row[0],row[1],row[2],value))
        
    daily_category_summary=new_daily_category_summary

    return render_template("history.html",category_summary=category_summary,daily_category_summary=daily_category_summary,
                           ctx1_period=ctx1_period,ctx1_unit=ctx1_unit,ctx2_period=ctx2_period,ctx2_unit=ctx2_unit)
    

if __name__ == "__main__":
    app.run(debug=True)