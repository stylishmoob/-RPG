from flask import Blueprint, jsonify, session

from backend.utils.decorators import user_required
from backend.utils.auth_utils import get_current_user_id

from backend.queries.categories_queries import (
    get_user_categories,
)

from backend.queries.statuses_queries import (
    get_user_statuses,
    get_user_achievements,
    get_user_jobs,
    get_user_by_id
)

from backend.queries.time_logs_queries import(
    get_today_logs,
    get_time_logs,
)


home_bp = Blueprint("home", __name__)

@home_bp.route("/api/home")
@user_required
def api_home():
    user_id=get_current_user_id()

    logs=get_time_logs(user_id)
    user_categories=get_user_categories(user_id)
    today_logs=get_today_logs(user_id)
    user_statuses=get_user_statuses(user_id)
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
    "user_statuses":[{
        "id":row["status_id"],
        "name": row["status_name"],
        "value": row["status_value"],
        "type": row["status_type"],
        }
        for row in user_statuses
        ],

    "user_achievements": [
        {
        "achievement_name":row["achievement_name"],
        "title_name":row["title_name"],
        }
        for row in user_achievements
        ],

    "user_categories": [
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