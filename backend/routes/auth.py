import sqlite3

from flask import Blueprint, jsonify, session,request

from werkzeug.security import check_password_hash,generate_password_hash

from backend.queries.users_queries import(
    get_user_by_name,
    create_user,
)
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/login",methods=["POST"])
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

@auth_bp.route("/api/register",methods=["POST"])
def api_register():
    data=request.get_json()

    user_name=data["user_name"]
    password=data["password"]

    password_hash =generate_password_hash(password)

    try:
        create_user(user_name,password_hash)

    except sqlite3.IntegrityError:
        return jsonify({
            "success": False,
            "message": "そのユーザー名は既に使われています"
        }),409
    
    return jsonify({
        "success":True,
        "message":"登録完了しました"
    }),201

@auth_bp.route("/api/logout",methods=["POST"])
def api_logout():
    session.clear()

    return jsonify({
        "success": True
    })
