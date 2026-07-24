from flask import Blueprint, jsonify,request
import csv
from backend.utils.decorators import admin_required

from backend.queries.admin.job_queries import (
    get_job_requirements,
    get_master_jobs,
    add_admin_job,
    edit_admin_job,
    import_jobs_csv
)

from backend.queries.admin.status_queries import(
    get_master_statuses,
)

admin_job_bp=Blueprint(
    "admin_job",
    __name__,
    url_prefix="/api/admin/jobs"
)

@admin_job_bp.get("/api/admin/jobs")
@admin_required
def api_admin_jobs():
    master_statuses=get_master_statuses()
    master_jobs=get_master_jobs()
    job_requirements=get_job_requirements()

    return jsonify({
        "success":True,

        "masterJobs":[{
            "id":row["id"],
            "job_name":row["job_name"],
            "is_active":row["is_active"],
            "is_default":row["is_default"],
         } for row in master_jobs 
        ],
        "jobRequirements":[{
            "id":row["id"],
            "job_id":row["job_id"],
            "required_status_id":row["required_status_id"],
            "required_status_name":row["required_status_name"],
            "required_status_value":row["required_status_value"],
            "is_active":row["is_active"],
        } for row in job_requirements
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
    
@admin_job_bp.post("/api/admin/jobs/add")
@admin_required
def api_admin_add_job():
    data=request.get_json()

    job_name=data["job_name"]
    requirements=data["requirements"]

    add_admin_job(job_name,requirements)

    return jsonify({
        "success":True,
    }
    )

@admin_job_bp.post("/api/admin/jobs/edit")
@admin_required
def api_admin_edit_job():
    data=request.get_json()

    job_id=data["job_id"]
    job_name=data["job_name"]
    is_active=data["is_active"]
    is_default=data["is_default"]
    requirements=data["requirements"]
    
    edit_admin_job(job_id,job_name,is_active,is_default,requirements)

    return jsonify({
        "success":True,
    }
    )

@admin_job_bp.post("/api/admin/jobs/import")
@admin_required
def api_admin_import_jobs():
    csv_file=request.files.get("file")
    
    try:
        result=import_jobs_csv(csv_file)
        
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