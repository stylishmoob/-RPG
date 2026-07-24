from flask import Blueprint, jsonify,request
from backend.utils.decorators import user_required
from backend.utils.auth_utils import get_current_user_id

from backend.queries.time_logs_queries import(
    save_time_logs,
)
from backend.queries.statuses_queries import(
    status_cir,
)
from backend.queries.jobs_queries import(
    check_user_job,
)
from backend.queries.achievements_queries import(
    check_category_achievement,
)

action_bp = Blueprint("save_action",__name__)

@action_bp.post("/api/save_action")
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

    return jsonify ({
        "success":True
    })