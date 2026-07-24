from flask import Blueprint, jsonify,request
import csv
from backend.utils.decorators import admin_required

from backend.queries.admin.category_queries import(
    get_master_categories,
    add_master_category,
    edit_master_category,
    import_category_csv,
)


admin_category_bp=Blueprint(
    "admin_category",
    __name__,
    url_prefix="/api/admin/categories"
)

@admin_category_bp.get("")
@admin_required
def api_admin_categories():
    master_categories=get_master_categories()
    
    return jsonify({
        "success": True,
        "MasterCategories":[{
            "id":row["id"],
            "name":row["category_name"],
            "is_active":row["is_active"],
        }
        for row in master_categories
        ],
    })

@admin_category_bp.post("/add")
@admin_required
def api_admin_add_categories():
    category_name=request.get_json()

    add_master_category(category_name)

    return jsonify({
        "success":True,
    })

@admin_category_bp.post("/edit")
@admin_required
def api_admin_edit_categories():
    data=request.get_json()

    category_id=data["category_id"]
    category_name=data["category_name"]
    category_is_active=data["category_is_active"]

    edit_master_category(category_id,category_name,category_is_active)

    return jsonify({
        "success":True,
    })

@admin_category_bp.post("/import")
@admin_required
def api_admin_import_categories():
    csv_file=request.files.get("file")
    
    try:
        result=import_category_csv(csv_file)
        
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
    