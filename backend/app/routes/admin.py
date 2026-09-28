from flask import Blueprint, jsonify,request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models import User, Job


admin = Blueprint("admin", __name__, url_prefix="/api/admin")
def admin_required():
    """
    Checks that the currently authenticated user is an admin.
    Returns the user if authorized, otherwise returns an error response.
    """

    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)

    if not user:
        return None, (jsonify({
            "error": True,
            "message": "User not found"
        }), 404)

    if user.role != "admin":
        return None, (jsonify({
            "error": True,
            "message": "Admin access required"
        }), 403)

    return user, None


@admin.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():

    user, error = admin_required()

    if error:
        return error

    total_users = User.query.count()

    total_clients = User.query.filter_by(
        role="client"
    ).count()

    total_vendors = User.query.filter_by(
        role="vendor"
    ).count()

    total_admins = User.query.filter_by(
        role="admin"
    ).count()

    active_users = User.query.filter_by(
        status="active"
    ).count()

    suspended_users = User.query.filter_by(
        status="suspended"
    ).count()

    total_jobs = Job.query.count()

    open_jobs = Job.query.filter_by(
        status="open"
    ).count()

    active_jobs = Job.query.filter_by(
        status="in_progress"
    ).count()

    awaiting_approval = Job.query.filter_by(
        status="awaiting_approval"
    ).count()

    completed_jobs = Job.query.filter_by(
        status="completed"
    ).count()

    return jsonify({
        "error": False,
        "data": {
            "users": {
                "total": total_users,
                "clients": total_clients,
                "vendors": total_vendors,
                "admins": total_admins,
                "active": active_users,
                "suspended": suspended_users
            },
            "jobs": {
                "total": total_jobs,
                "open": open_jobs,
                "in_progress": active_jobs,
                "awaiting_approval": awaiting_approval,
                "completed": completed_jobs
            }
        }
    }), 200
# GET USERS
@admin.route("/users", methods=["GET"])
@jwt_required()
def get_users():

    user, error = admin_required()

    if error:
        return error

    role = request.args.get("role")
    search = request.args.get("search")

    query = User.query

    # Filter by role
    if role:
        query = query.filter_by(role=role)

    # Search by name or email
    if search:
        search_term = f"%{search}%"

        query = query.filter(
            db.or_(
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                User.email.ilike(search_term)
            )
        )

    users = query.order_by(
        User.created_at.desc()
    ).all()

    users_data = []

    for item in users:
        users_data.append({
            "id": item.id,
            "first_name": item.first_name,
            "last_name": item.last_name,
            "email": item.email,
            "role": item.role,
            "phone": item.phone,
            "profile_image": item.profile_image,
            "status": item.status,
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat()
        })

    return jsonify({
        "error": False,
        "data": users_data
    }), 200

# GET SINGLE USER
@admin.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):

    user, error = admin_required()

    if error:
        return error

    target_user = User.query.get(user_id)

    if not target_user:
        return jsonify({
            "error": True,
            "message": "User not found"
        }), 404

    return jsonify({
        "error": False,
        "data": {
            "id": target_user.id,
            "first_name": target_user.first_name,
            "last_name": target_user.last_name,
            "email": target_user.email,
            "role": target_user.role,
            "phone": target_user.phone,
            "profile_image": target_user.profile_image,
            "status": target_user.status,
            "created_at": target_user.created_at.isoformat(),
            "updated_at": target_user.updated_at.isoformat()
        }
    }), 200
# Suspend or Activate User    
@admin.route("/users/<int:user_id>/status", methods=["PUT"])
@jwt_required()
def update_user_status(user_id):

    admin_user, error = admin_required()

    if error:
        return error

    target_user = User.query.get(user_id)

    if not target_user:
        return jsonify({
            "error": True,
            "message": "User not found"
        }), 404

    data = request.get_json()

    status = data.get("status")

    if status not in ["active", "suspended"]:
        return jsonify({
            "error": True,
            "message": "Status must be active or suspended"
        }), 400

    # Prevent admin from suspending themselves
    if target_user.id == admin_user.id:
        return jsonify({
            "error": True,
            "message": "You cannot change your own status"
        }), 400

    target_user.status = status

    db.session.commit()

    return jsonify({
        "error": False,
        "message": f"User {status} successfully",
        "data": {
            "id": target_user.id,
            "status": target_user.status
        }
    }), 200
# DELETE A USER
@admin.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):

    admin_user, error = admin_required()

    if error:
        return error

    target_user = User.query.get(user_id)

    if not target_user:
        return jsonify({
            "error": True,
            "message": "User not found"
        }), 404

    if target_user.id == admin_user.id:
        return jsonify({
            "error": True,
            "message": "You cannot delete your own account"
        }), 400

    db.session.delete(target_user)
    db.session.commit()

    return jsonify({
        "error": False,
        "message": "User deleted successfully"
    }), 200
    
#GET ALL JOBS
@admin.route("/jobs", methods=["GET"])
@jwt_required()
def get_jobs():

    admin_user, error = admin_required()

    if error:
        return error

    status = request.args.get("status")
    search = request.args.get("search")

    query = Job.query

    # Filter by status
    if status:
        query = query.filter_by(status=status)

    # Search by job title
    if search:
        search_term = f"%{search}%"

        query = query.filter(
            Job.title.ilike(search_term)
        )

    jobs = query.order_by(
        Job.created_at.desc()
    ).all()

    jobs_data = []

    for job in jobs:

        jobs_data.append({
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "scope": job.scope,
            "duration": job.duration,
            "experience_level": job.experience_level,
            "budget": float(job.budget),
            "status": job.status,

            "client": {
                "id": job.client.id,
                "first_name": job.client.first_name,
                "last_name": job.client.last_name,
                "email": job.client.email
            },

            "category": {
                "id": job.category.id,
                "name": job.category.name
            },

            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat()
        })

    return jsonify({
        "error": False,
        "data": jobs_data
    }), 200
    

# GET ONE JOB
@admin.route("/jobs/<int:job_id>", methods=["GET"])
@jwt_required()
def get_job(job_id):

    admin_user, error = admin_required()

    if error:
        return error

    job = Job.query.get(job_id)

    if not job:
        return jsonify({
            "error": True,
            "message": "Job not found"
        }), 404

    return jsonify({
        "error": False,
        "data": {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "skills_required": job.skills_required,
            "scope": job.scope,
            "duration": job.duration,
            "experience_level": job.experience_level,
            "budget": float(job.budget),
            "status": job.status,

            "client": {
                "id": job.client.id,
                "first_name": job.client.first_name,
                "last_name": job.client.last_name,
                "email": job.client.email
            },

            "category": {
                "id": job.category.id,
                "name": job.category.name
            },

            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat()
        }
    }), 200
