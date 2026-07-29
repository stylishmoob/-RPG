from flask import Blueprint, jsonify, request

from backend.utils.decorators import admin_required

from backend.queries.admin.user_queries import (
    get_admin_users,
    edit_admin_user_active,
    reset_admin_user_data,
    delete_admin_user,
)

admin_user_bp=Blueprint(
    "admin_user",
    __name__,
    url_prefix="/api/admin/users"
)

reset_user_data_bp=Blueprint(
    "reset_user_data",
    __name__,
)

@admin_user_bp.get("")
@admin_required
def api_admin_users():
    admin_users=get_admin_users()

    return jsonify({
        "success":True,
        "users":[
            {
                "id":str(row["id"]),
                "username":row["user_name"],
                "userLevel":str(row["user_level"]),
                "userCurrentJob":row["current_job_name"],
                "isAdmin":bool(row["is_admin"]),
                "isActive":bool(row["is_active"]),
            }
            for row in admin_users
        ],
    })

@admin_user_bp.post("/edit")
@admin_required
def api_admin_edit_user():
    data=request.get_json()

    user_id=data["user_id"]
    is_active=data["is_active"]

    result=edit_admin_user_active(user_id,is_active)

    return jsonify({
        "success":True,
        **result,
    })

@admin_user_bp.post("/delete")
@admin_required
def api_admin_delete_user():
    data=request.get_json()

    user_id=data.get("user_id")

    if user_id is None:
        return jsonify({
            "success":False,
            "message":"user_idがありません",
        }), 400

    try:
        result=delete_admin_user(user_id)
    except ValueError as error:
        return jsonify({
            "success":False,
            "message":str(error),
        }), 400

    return jsonify({
        "success":True,
        **result,
    })

@reset_user_data_bp.post("/api/reset_user_data")
@admin_required
def api_reset_user_data():
    data=request.get_json()

    user_id=data.get("user_id")

    if user_id is None:
        return jsonify({
            "success":False,
            "message":"user_idがありません",
        }), 400

    try:
        result=reset_admin_user_data(user_id)
    except ValueError as error:
        return jsonify({
            "success":False,
            "message":str(error),
        }), 400

    return jsonify({
        "success":True,
        **result,
    })
