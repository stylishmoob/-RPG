from flask import Blueprint, jsonify,request
import csv
from backend.utils.decorators import admin_required

from backend.queries.admin.achievement_queries import(
    get_master_achievements,
    add_master_achievement,
    edit_master_achievement,
    import_achievement_csv,
)

from backend.queries.admin.category_queries import(
    get_master_categories,
)

admin_achievement_bp=Blueprint(
    "admin_achievement",
    __name__,
    url_prefix="/api/admin/achievements"
)

@admin_achievement_bp.get("")
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

    
@admin_achievement_bp.post("/add")
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

@admin_achievement_bp.post("/edit")
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

@admin_achievement_bp.post("/import")
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