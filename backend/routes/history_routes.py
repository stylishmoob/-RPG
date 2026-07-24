from flask import Blueprint, jsonify,request
from backend.utils.decorators import user_required
from backend.utils.auth_utils import get_current_user_id
from backend.queries.time_logs_queries import(
    get_category_summary,
    get_daily_summary,
)

history_bp = Blueprint("history", __name__)

@history_bp.get("/api/history")
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