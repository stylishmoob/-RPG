from functools import wraps

from flask import session,jsonify

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            session.clear()
            return jsonify({
                "success": False,
                "message": "login required"
            }), 401

        if session.get("is_admin") != 1:
            return jsonify({
                "success": False,
                "message": "admin required"
            }), 403

        return func(*args, **kwargs)

    return wrapper

def user_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            session.clear()
            return jsonify({
                "success": False,
                "message": "login required"
            }), 401
        
        return func(*args, **kwargs)
    
    return wrapper