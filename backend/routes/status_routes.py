from flask import Blueprint, jsonify,request,session
from backend.utils.decorators import user_required
from backend.utils.auth_utils import get_current_user_id
from backend.queries.statuses_queries import (
    get_user_statuses,
    get_user_by_id
)
from backend.queries.jobs_queries import (
    get_user_jobs,
)

from backend.queries.achievements_queries import (
    get_user_achievements,
)

from backend.queries.time_logs_queries import(
    get_time_logs,
)

status_bp = Blueprint("status",__name__)

@status_bp.get("/api/status")
@user_required
def api_status():
    user_id=get_current_user_id()

    logs=get_time_logs(user_id)
    user_status=get_user_statuses(user_id)
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

        "is_admin": session.get("is_admin") == 1,
})