from flask import Blueprint, jsonify,request
from backend.utils.decorators import user_required
from backend.utils.auth_utils import get_current_user_id
from backend.queries.categories_queries import (
    get_user_categories,
    get_user_master_categories,
    delete_user_category,
    add_user_category,
)

category_bp = Blueprint("category", __name__)

@category_bp.get("/api/category")
@user_required
def api_category():
    user_id=get_current_user_id()
    
    user_categories=get_user_categories(user_id)
    master_categories=get_user_master_categories()

    return jsonify({
        "success":True,

        "user_categories": [
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

@category_bp.delete("/api/category/<int:category_id>")
@user_required
def api_category_delete(category_id):
    user_id=get_current_user_id()
    delete_user_category(user_id,category_id)

    return jsonify ({
        "success":True,
    })
    
@category_bp.post("/api/category/add")
@user_required
def api_category_add():
    data= request.get_json()

    user_id=get_current_user_id()
    master_category_id=data["master_category_id"]
    add_user_category(user_id,master_category_id)

    return jsonify({
        "success":True,
    })