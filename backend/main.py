import sqlite3
from flask import Flask,render_template,request,redirect,url_for,session,abort,jsonify
import os
import csv
import io
from werkzeug.security import check_password_hash
from backend.queries import get_time_logs,get_user_categories,get_user_status,get_user_achievements, get_user_jobs,save_time_logs,add_user_category,delete_user_category,get_today_logs,get_category_summary,check_category_achievement,get_daily_summary,status_cir,check_user_job,get_master_categories,add_master_category,get_master_status_rules,add_status_rules,get_master_achievements,add_master_achievement,get_master_statuses,get_master_jobs_requirement,add_master_job,create_user
from backend.queries import edit_master_category,add_master_status,edit_master_status,delete_status_rules,edit_master_achievement,toggle_master_job,get_user_master_categories,get_user_by_name,get_user_by_id,import_status_csv,import_category_csv,import_achievement_csv
from backend.decorators import user_required,admin_required
app=Flask(__name__)
app.secret_key ="hoge"

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_NAME=os.path.join(BASE_DIR,"rpg_table.db")

def get_current_user_id():
    return session["user_id"]

@app.route("/api/home",methods=["GET"])
@user_required
def api_home():
    
    user_id=get_current_user_id()

    logs=get_time_logs(user_id)
    user_categories=get_user_categories(user_id)
    today_logs=get_today_logs(user_id)
    user_status=get_user_status(user_id)
    user_achievements=get_user_achievements(user_id)
    user_job=get_user_jobs(user_id)
    user=get_user_by_id(user_id)
    user_name=user["user_name"]
    user_level=float(user["user_level"])
    current_exp=round((user_level-int(user["user_level"]))*100)

    next_exp=100

    exp_percent=min(current_exp/next_exp*100,100)

    job_name=user_job[1]
    
    return jsonify({
    "success": True,
    "user": {
        "id": user_id,
        "name": user_name,
        "level": int(user_level),
    },
    "exp": {
        "current": current_exp,
        "next": next_exp,
        "percent": exp_percent,
    },
    "job": {
        "name": job_name if user_job else None,
    },
    "status":[{
        "id":row["status_id"],
        "name": row["status_name"],
        "value": row["status_value"],
        "type": row["status_type"],
        }
        for row in user_status
        ],

    "achievements": [
        {
        "achievement_name":row["achievement_name"],
        "title_name":row["title_name"],
        }
        for row in user_achievements
        ],

    "categories": [
        {
        "id":row["category_id"],
        "name":row["category_name"],  
        }
        for row in user_categories
        ],

    "today_logs":[
        {
        "category_id":row["category_id"],
        "category_name":row["category_name"],
        "start_time":row["start_time"],
        "end_time":row["end_time"], 
        "duration_seconds":row["duration_seconds"],
        }
        for row in today_logs
        ],

    "is_admin": session.get("is_admin") == 1,
})

@app.route("/save_action",methods=["POST"])
@user_required
def save_action():
    user_id=get_current_user_id()

    data=request.get_json()

    selected_category_id=data["category_id"]
    start_time=data["start_time"]
    end_time=data["end_time"]
    duration_seconds=int(data["duration_seconds"])

    save_time_logs(user_id,selected_category_id,start_time,end_time,duration_seconds)
    status_cir(selected_category_id,duration_seconds,user_id)
    new_achievement_count=check_category_achievement(user_id)
    check_user_job(user_id)

    logs=get_time_logs(user_id)
    user_categories=get_user_categories(user_id)
    today_logs=get_today_logs(user_id)
    user_status=get_user_status(user_id)
    user_achievements=get_user_achievements(user_id)
    user_job=get_user_jobs(user_id)
    user=get_user_by_id(user_id)
    user_name=user["user_name"]
    user_level=float(user["user_level"])
    current_exp=round((user_level-int(user["user_level"]))*100)

    next_exp=100

    exp_percent=min(current_exp/next_exp*100,100)

    job_name=user_job[1]

    return jsonify({
    "success": True,
    "user": {
        "id": user_id,
        "name": user_name,
        "level": int(user_level),
    },
    "exp": {
        "current": current_exp,
        "next": next_exp,
        "percent": exp_percent,
    },
    "job": {
        "name": job_name if user_job else None,
    },
    "status":[{
        "id":row["status_id"],
        "name": row["status_name"],
        "value": row["status_value"],
        "type": row["status_type"],
        }
        for row in user_status
        ],

    "achievements": [
        {
        "achievement_name":row["achievement_name"],
        "title_name":row["title_name"],
        }
        for row in user_achievements
        ],

    "categories": [
        {
        "id":row["category_id"],
        "name":row["category_name"],  
        }
        for row in user_categories
        ],

    "today_logs":[
        {
        "category_id":row["category_id"],
        "category_name":row["category_name"],
        "start_time":row["start_time"],
        "end_time":row["end_time"], 
        "duration_seconds":row["duration_seconds"],
        }
        for row in today_logs
        ],
    })

   
@app.route("/api/category",methods=["GET"])
@user_required
def api_category():
    user_id=get_current_user_id()
    
    user_categories=get_user_categories(user_id)
    master_categories=get_user_master_categories()

    return jsonify({
        "success":True,

        "categories": [
        {
        "id":row["category_id"],
        "name":row["category_name"],  
        }
        for row in user_categories
        ],

        "master_categories": [
        {
        "id":row["id"],
        "name":row["category_name"],
        }
        for row in master_categories
        ],
    })

@app.route("/api/category/<int:category_id>",methods=["DELETE"])
@user_required
def api_category_delete(category_id):
    user_id=get_current_user_id()
    delete_user_category(user_id,category_id)

    return jsonify ({
        "success":True,
    })
    
@app.route("/api/category/add",methods=["POST"])
@user_required
def api_category_add():
    data= request.get_json()
    user_id=get_current_user_id()
    master_category_id=data["master_category_id"]
    add_user_category(user_id,master_category_id)

    return jsonify({
        "success":True,
    })
   
@app.route("/api/history",methods=["GET"])
@user_required
def api_history():
    user_id=get_current_user_id()
    
    ctx1_period=request.args.get("ctx1Period", "all")
    ctx2_period=request.args.get("ctx2Period", "all")

    category_summary=get_category_summary(ctx1_period,user_id)
    daily_category_summary=get_daily_summary(ctx2_period,user_id)
   
    return jsonify({
        "success": True,
        "categorySummary":[{
            "category_id":row["category_id"],
            "category_name":row["category_name"],
            "category_total_seconds":row["category_total_seconds"],
        }
            for row in category_summary
        ],

        "dailyCategorySummary":[{
            "category_id":row["category_id"],
            "category_name":row["category_name"],
            "log_date":row["log_date"],
            "daily_total_seconds":row["daily_total_seconds"],
        }
            for row in daily_category_summary
        ],
    })

@app.route("/api/status",methods=["GET"])
@user_required
def api_status():
    user_id=get_current_user_id()

    user_status=get_user_status(user_id)
    user_achievements=get_user_achievements(user_id)
    user_job=get_user_jobs(user_id)
    user=get_user_by_id(user_id)
    user_name=user["user_name"]
    user_level=float(user["user_level"])
    current_exp=round((user_level-int(user["user_level"]))*100)

    next_exp=100

    exp_percent=min(current_exp/next_exp*100,100)

    job_name=user_job[1]
    
    return jsonify({
    "success": True,
    "user": {
        "id": user_id,
        "name": user_name,
        "level": int(user_level),
    },
    "exp": {
        "current": current_exp,
        "next": next_exp,
        "percent": exp_percent,
    },
    "job": {
        "name": job_name if user_job else None,
    },
    "status":[{
        "id":row["status_id"],
        "name": row["status_name"],
        "value": row["status_value"],
        "type": row["status_type"],
        }
        for row in user_status
        ],

    "achievements": [
        {
        "achievement_name":row["achievement_name"],
        "title_name":row["title_name"],
        }
        for row in user_achievements
        ],

    "is_admin": session.get("is_admin") == 1,
})


@app.route("/api/admin/categories",methods=["GET"])
@admin_required
def api_admin_categories():
    master_categories=get_master_categories()
    
    return jsonify({
        "success": True,
        "MasterCategories":[{
            "id":row["id"],
            "name":row["category_name"],
            "is_active":row["is_active"],
        }
        for row in master_categories
        ],
    })

@app.route("/api/admin/categories/add",methods=["POST"])
@admin_required
def api_admin_add_categories():
    category_name=request.get_json()

    add_master_category(category_name)

    return jsonify({
        "success":True,
    })

@app.route("/api/admin/categories/edit",methods=["POST"])
@admin_required
def api_admin_edit_categories():
    data=request.get_json()

    category_id=data["category_id"]
    category_name=data["category_name"]
    category_is_active=data["category_is_active"]

    edit_master_category(category_id,category_name,category_is_active)

    return jsonify({
        "success":True,
    })

@app.route("/api/admin/categories/import",methods=["POST"])
@admin_required
def api_admin_import_categories():
    csv_file=request.files.get("file")
    
    try:
        result=import_category_csv(csv_file)
        
        status_code=200 if result["success"] else 400

        return jsonify(result), status_code 

    except UnicodeDecodeError:
        return jsonify({
            "success": False,
            "message": "文字コードを読み取れませんでした。UTF-8形式で保存してください",
        }), 400

    except csv.Error:
        return jsonify({
            "success": False,
            "message": "CSVの形式が正しくありません",
        }), 400

    except Exception as error:
        print(error)

        return jsonify({
            "success": False,
            "message": "CSVの取り込みに失敗しました",
        }), 500
    

@app.route("/api/admin/statuses",methods=["GET"])
@admin_required
def api_admin_statuses():
    master_statuses=get_master_statuses()

    return jsonify({
        "success":True,
        "masterStatuses":[
            {
            "id":row["id"],
            "name":row["status_name"],
            "type":row["status_type"],
            "isActive":row["is_active"]
            }
            for row in master_statuses
        ],
    })

@app.route("/api/admin/statuses/add",methods=["POST"])
@admin_required
def api_admin_add_status():
    status_name=request.form["status_name"]
    status_type=request.form["status_type"]

    add_master_status(status_name,status_type)

    return jsonify({
        "success":True
    })

@app.route("/api/admin/statuses/edit",methods=["POST"])
@admin_required
def api_admin_edit_status():
    data=request.get_json()

    status_id=data["status_id"]
    status_name=data["status_name"]
    status_type=data["status_type"]
    is_active=data["status_is_active"]

    edit_master_status(status_id,status_name,status_type,is_active)
    
    return jsonify({
        "success":True
    })

@app.route("/api/admin/statuses/import",methods=["POST"])
@admin_required
def api_admin_import_status():
    csv_file=request.files.get("file")
    
    try:
        result=import_status_csv(csv_file)
        
        status_code=200 if result["success"] else 400

        return jsonify(result), status_code 

    except UnicodeDecodeError:
        return jsonify({
            "success": False,
            "message": "文字コードを読み取れませんでした。UTF-8形式で保存してください",
        }), 400

    except csv.Error:
        return jsonify({
            "success": False,
            "message": "CSVの形式が正しくありません",
        }), 400

    except Exception as error:
        print(error)

        return jsonify({
            "success": False,
            "message": "CSVの取り込みに失敗しました",
        }), 500

@app.route("/api/admin/status_rules",methods=["GET"])
@admin_required
def api_admin_status_rules():
    status_rules=get_master_status_rules()
    master_categories=get_master_categories()
    master_statuses=get_master_statuses()

    return jsonify({
        "success":True,
        "statusRules":[{
            "id":row["id"],
            "category_id":row["category_id"],
            "category_name":row["category_name"],
            "status_id":row["status_id"],
            "status_name":row["status_name"],
            "gain_per_hours":row["gain_per_hours"],
            "is_active":row["is_active"],}
            for row in status_rules
            ],
        "masterCategories":[{
            "id":row["id"],
            "name":row["category_name"],
            "is_active":row["is_active"],
        }
        for row in master_categories
        ],
        "masterStatuses":[
            { 
            "id":row["id"],
            "name":row["status_name"],
            "type":row["status_type"],
            "is_active":row["is_active"]
            }
        for row in master_statuses
        ],
   })
@app.route("/admin/status_rules/add",methods=["POST"])
def admin_add_status_rules():
    category_id=request.form["category_id"]
    status_id=request.form["status_id"]
    gain_per_hours=request.form["gain_per_hours"]

    add_status_rules(category_id,status_id,gain_per_hours)

    return redirect(url_for("admin_status_rules"))

@app.route("/admin/status_rules/delete",methods=["POST"])
def admin_delete_status_rules():
    category_id=request.form["category_id"]
    status_id=request.form["status_id"]

    delete_status_rules(category_id,status_id)

    return redirect(url_for("admin_status_rules"))



@app.route("/api/admin/achievements",methods=["GET"])
@admin_required
def api_admin_achievements():
    master_achievements=get_master_achievements()
    master_categories=get_master_categories()

    return jsonify({
        "success":True,
        "achievements":[
        {
        "id":row["id"],
        "category_id":row["category_id"],
        "category_name":row["category_name"],
        "required_hours":row["required_hours"],
        "achievement_name":row["achievement_name"],
        "title_name":row["title_name"],
        "is_active":row["is_active"],
        }
        for row in master_achievements
        ],
        "mastercategories":[{
            "id":row["id"],
            "name":row["category_name"],
            "is_active":row["is_active"],
        }
        for row in master_categories
        ],})

    
@app.route("/api/admin/achievements/add",methods=["POST"])
@admin_required
def api_admin_add_achievements():

    data=request.get_json()

    required_category_id=data("category_id")
    required_hours=data("required_hours")
    achievement_name=data("achievement_name")
    title_name=data("title_name")

    add_master_achievement(required_category_id,required_hours,achievement_name,title_name)

    return jsonify({
        "success":True,
    })

@app.route("/api/admin/achievements/edit",methods=["POST"])
@admin_required
def api_admin_edit_achievements():
    
    data=request.get_json()

    achievement_id=data("achievement_id")
    required_category_id=data("category_id")
    required_hours=data("required_hours")
    achievement_name=data("achievement_name")
    title_name=data("title_name")
    is_active=data("is_active")


    edit_master_achievement(achievement_id,required_category_id,required_hours,achievement_name,title_name,is_active)

    return jsonify({
        "success":True,
    })

@app.route("/api/admin/achievements/import",methods=["POST"])
@admin_required
def api_admin_import_achievements():
    csv_file=request.files.get("file")
    
    try:
        result=import_achievement_csv(csv_file)
        
        status_code=200 if result["success"] else 400

        return jsonify(result), status_code 

    except UnicodeDecodeError:
        return jsonify({
            "success": False,
            "message": "文字コードを読み取れませんでした。UTF-8形式で保存してください",
        }), 400

    except csv.Error:
        return jsonify({
            "success": False,
            "message": "CSVの形式が正しくありません",
        }), 400

    except Exception as error:
        print(error)

        return jsonify({
            "success": False,
            "message": "CSVの取り込みに失敗しました",
        }), 500

@app.route("/admin/jobs")
def admin_jobs():
    if session.get("is_admin") != 1:
        abort(403)
    master_statuses=get_master_statuses()
    master_jobs=get_master_jobs_requirement()
    
    return render_template("admin/jobs.html",master_statuses=master_statuses,master_jobs=master_jobs)

@app.route("/admin/jobs/add",methods=["POST"])
def admin_add_jobs():
    job_name=request.form["job_name"]
    status_id_1=request.form["status_id_1"]
    required_status1_value=request.form["required_status1_value"]
    status_id_2=request.form["status_id_2"]
    required_status2_value=request.form["required_status2_value"]

    add_master_job(job_name,status_id_1,required_status1_value,status_id_2,required_status2_value)

    return redirect(url_for("admin_jobs"))

@app.route("/admin/jobs/toggle",methods=["POST"])
def admin_toggle_jobs():
    job_id=request.form["job_id"]

    toggle_master_job(job_id)

    return redirect(url_for("admin_jobs"))


@app.route("/api/login",methods=["POST"])
def api_login():
    data=request.get_json()

    user_name=data["user_name"]
    password=data["password"]

    user=get_user_by_name(user_name)

    if user and check_password_hash(user["password_hash"],password):
        session["user_id"] = user["id"]

        return jsonify({
            "success":True
        })
    
    return jsonify({
    "success": False,
    "message": "ユーザー名またはパスワードが違います"
}), 401

@app.route("/register",methods=["GET","POST"])
def register():

    if request.method=="POST":
        user_name=request.form["user_name"]
        create_user(user_name)

        return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route("/api/logout",methods=["POST"])
def api_logout():
    session.clear()

    return jsonify({
        "success": True
    })

if __name__ == "__main__":
    app.run(debug=True)

