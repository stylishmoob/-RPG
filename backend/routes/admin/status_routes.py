from flask import Blueprint, jsonify,request
import csv
from backend.utils.decorators import admin_required

from backend.queries.admin.status_queries import(
    get_master_statuses,
    add_master_status,
    edit_master_status,
    import_status_csv,  
)

admin_status_bp=Blueprint(
    "admin_status",
    __name__,
    url_prefix="/api/admin/statuses"
)

@admin_status_bp.get("")
@admin_required
def api_admin_statuses():
    master_statuses=get_master_statuses()

    return jsonify({
        "success":True,
        "masterStatuses":[
            {
            "id":row["id"],
            "name":row["status_name"],
            "type":row["status_type"],
            "isActive":row["is_active"]
            }
            for row in master_statuses
        ],
    })

@admin_status_bp.post("/add")
@admin_required
def api_admin_add_status():
    status_name=request.form["status_name"]
    status_type=request.form["status_type"]

    add_master_status(status_name,status_type)

    return jsonify({
        "success":True
    })

@admin_status_bp.post("/edit")
@admin_required
def api_admin_edit_status():
    data=request.get_json()

    status_id=data["status_id"]
    status_name=data["status_name"]
    status_type=data["status_type"]
    is_active=data["status_is_active"]

    edit_master_status(status_id,status_name,status_type,is_active)
    
    return jsonify({
        "success":True
    })

@admin_status_bp.post("/import")
@admin_required
def api_admin_import_status():
    csv_file=request.files.get("file")
    
    try:
        result=import_status_csv(csv_file)
        
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