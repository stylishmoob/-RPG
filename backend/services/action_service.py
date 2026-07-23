from flask import Blueprint, jsonify,request
from backend.utils.decorators import user_required
from backend.utils.auth_utils import get_current_user_id

from backend.queries.time_logs_queries import(
    save_time_logs,
)


action_bp = Blueprint("save_action",__name__)

@action_bp.post("/api/save_action",methods=["POST"])
@user_required
def api_save_action():
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
    user_jobs=get_user_jobs(user_id)
    user=get_user_by_id(user_id)
    
    user_level=float(user["user_level"])
    current_exp=round((user_level-int(user["user_level"]))*100)

    next_exp=100

    exp_percent=min(current_exp/next_exp*100,100)

    return jsonify({
        "success": True,
        "user": {
            "id": user["id"],
            "name": user["user_name"],
            "job": user["current_job_name"],
            "level": int(user_level),
        },
        "exp": {
            "current": current_exp,
            "next": next_exp,
            "percent": exp_percent,
        },
        "job":[{
            "id":row["job_id"],
            "name":row["job_name"],
            }
            for row in user_jobs
            ],
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