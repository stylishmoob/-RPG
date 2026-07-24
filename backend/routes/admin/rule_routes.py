from flask import Blueprint, jsonify,request
import csv
from backend.utils.decorators import admin_required

from backend.queries.admin.rule_queries import(
    get_master_status_rules,
    add_status_rules,
    edit_status_rules,
    import_status_rules_csv
)

from backend.queries.admin.status_queries import(
    get_master_statuses,
)

from backend.queries.admin.category_queries import(
    get_master_categories,
)

admin_rule_bp=Blueprint(
    "admin_rule",
    __name__,
    url_prefix="/api/admin/status_rules"
)

@admin_rule_bp.get("")
@admin_required
def api_admin_status_rules():
    status_rules=get_master_status_rules()
    master_categories=get_master_categories()
    master_statuses=get_master_statuses()

    return jsonify({
        "success":True,
        "statusRules":[{
            "id":row["id"],
            "category_id":row["category_id"],
            "category_name":row["category_name"],
            "status_id":row["status_id"],
            "status_name":row["status_name"],
            "gain_per_hours":row["gain_per_hours"],
            "is_active":row["is_active"],}
            for row in status_rules
            ],
        "masterCategories":[{
            "id":row["id"],
            "name":row["category_name"],
            "is_active":row["is_active"],
        }
        for row in master_categories
        ],
        "masterStatuses":[
            { 
            "id":row["id"],
            "name":row["status_name"],
            "type":row["status_type"],
            "is_active":row["is_active"]
            }
        for row in master_statuses
        ],
   })
@admin_rule_bp.post("/add")
@admin_required
def api_admin_add_status_rules():
    data=request.get_json()

    category_id=data["category_id"]
    status_id=data["status_id"]
    gain_per_hours=data["gain_per_hours"]

    add_status_rules(category_id,status_id,gain_per_hours)

    return jsonify({
        "success":True
    })

@admin_rule_bp.post("/edit")
@admin_required
def api_admin_edit_status_rules():
    data=request.get_json()

    status_rules_id=data["id"]
    category_id=data["category_id"]
    status_id=data["status_id"]
    gain_per_hours=data["gain_per_hours"]
    status_rules_is_active=data["status_rules_is_active"]

    edit_status_rules(status_rules_id,category_id,status_id,gain_per_hours,status_rules_is_active)

    return jsonify({
        "success":True
    })

@admin_rule_bp.post("/import")
@admin_required
def api_admin_import_status_rules():
    csv_file=request.files.get("file")
    
    try:
        result=import_status_rules_csv(csv_file)
        
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