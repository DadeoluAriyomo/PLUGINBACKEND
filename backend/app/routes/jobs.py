from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.job import Job
from app.models.category import Category
from app.models.user import User


jobs = Blueprint("jobs", __name__)


@jobs.route("/jobs", methods=["POST"])
@jwt_required()
def create_job():

    # Get logged-in user's ID from JWT
    user_id = get_jwt_identity()

    # Find the user
    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "error": True,
            "message": "User not found",
            "data": None
        }), 404

    # Only clients can create jobs
    if user.role != "client":
        return jsonify({
            "error": True,
            "message": "Only clients can create jobs",
            "data": None
        }), 403

    # Get request data
    data = request.get_json()

    if not data:
        return jsonify({
            "error": True,
            "message": "Request body is required",
            "data": None
        }), 400

    # Required fields
    required_fields = [
        "category_id",
        "title",
        "skills_required",
        "scope",
        "duration",
        "experience_level",
        "budget"
    ]

    for field in required_fields:
        if field not in data or data[field] in [None, ""]:
            return jsonify({
                "error": True,
                "message": f"{field} is required",
                "data": None
            }), 400

    # Check category exists
    category = Category.query.get(data["category_id"])

    if not category:
        return jsonify({
            "error": True,
            "message": "Category not found",
            "data": None
        }), 404

    # Validate skills
    if not isinstance(data["skills_required"], list):
        return jsonify({
            "error": True,
            "message": "skills_required must be an array",
            "data": None
        }), 400

    if len(data["skills_required"]) == 0:
        return jsonify({
            "error": True,
            "message": "At least one skill is required",
            "data": None
        }), 400

    # Validate budget
    try:
        budget = float(data["budget"])

        if budget <= 0:
            raise ValueError

    except (ValueError, TypeError):
        return jsonify({
            "error": True,
            "message": "Budget must be a valid positive number",
            "data": None
        }), 400

    # Create job
    new_job = Job(
        client_id=user.id,
        category_id=category.id,
        title=data["title"].strip(),
        description=data.get("description", "").strip(),
        skills_required=data["skills_required"],
        scope=data["scope"].strip(),
        duration=data["duration"],
        experience_level=data["experience_level"],
        budget=budget,
        status="open"
    )

    db.session.add(new_job)
    db.session.commit()

    return jsonify({
        "error": False,
        "message": "Job created successfully",
        "data": {
            "id": new_job.id,
            "client_id": new_job.client_id,
            "category_id": new_job.category_id,
            "category": category.name,
            "title": new_job.title,
            "description": new_job.description,
            "skills_required": new_job.skills_required,
            "scope": new_job.scope,
            "duration": new_job.duration,
            "experience_level": new_job.experience_level,
            "budget": float(new_job.budget),
            "status": new_job.status,
            "created_at": new_job.created_at.isoformat()
        }
    }), 201
    
@jobs.route("/jobs/my-jobs", methods=["GET"])
@jwt_required()
def get_my_jobs():

    # Get logged-in user's ID
    user_id = get_jwt_identity()

    # Find user
    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "error": True,
            "message": "User not found",
            "data": None
        }), 404

    # Only clients can access their jobs
    if user.role != "client":
        return jsonify({
            "error": True,
            "message": "Only clients can access this endpoint",
            "data": None
        }), 403

    # Get jobs belonging to this client
    my_jobs = Job.query.filter_by(
        client_id=user.id
    ).order_by(
        Job.created_at.desc()
    ).all()

    jobs_data = []

    for job in my_jobs:
        jobs_data.append({
            "id": job.id,
            "category_id": job.category_id,
            "category": job.category.name,
            "title": job.title,
            "description": job.description,
            "skills_required": job.skills_required,
            "scope": job.scope,
            "duration": job.duration,
            "experience_level": job.experience_level,
            "budget": float(job.budget),
            "status": job.status,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat() if job.updated_at else None
        })

    return jsonify({
        "error": False,
        "message": "Jobs retrieved successfully",
        "data": jobs_data,
        "count": len(jobs_data)
    }), 200

@jobs.route("/jobs/available", methods=["GET"])
@jwt_required()
def get_available_jobs():
    user_id = get_jwt_identity()

    # Find the logged-in user
    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "error": True,
            "message": "User not found",
            "data": None
        }), 404

    # Only vendors can access available jobs
    if user.role != "vendor":
        return jsonify({
            "error": True,
            "message": "Only vendors can access available jobs",
            "data": None
        }), 403

    # Get the IDs of the vendor's selected categories
    category_ids = [category.id for category in user.categories]

    # If the vendor has no categories
    if not category_ids:
        return jsonify({
            "error": False,
            "message": "No jobs available because you have not selected any service categories",
            "data": [],
            "count": 0
        }), 200

    # Find open jobs belonging to the vendor's categories
    available_jobs = Job.query.filter(
        Job.category_id.in_(category_ids),
        Job.status == "open",
        Job.client_id != user.id
    ).order_by(Job.created_at.desc()).all()

    jobs_data = []

    for job in available_jobs:
        jobs_data.append({
            "id": job.id,
            "client_id": job.client_id,
            "category_id": job.category_id,
            "category": job.category.name,
            "title": job.title,
            "description": job.description,
            "skills_required": job.skills_required,
            "scope": job.scope,
            "duration": job.duration,
            "experience_level": job.experience_level,
            "budget": float(job.budget),
            "status": job.status,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat() if job.updated_at else None
        })

    return jsonify({
        "error": False,
        "message": "Available jobs retrieved successfully",
        "data": jobs_data,
        "count": len(jobs_data)
    }), 200
    
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models import Job, Bid




@jobs.route("/jobs/<int:job_id>/complete", methods=["PUT"])
@jwt_required()
def mark_job_complete(job_id):

    user_id = int(get_jwt_identity())

    job = Job.query.get(job_id)

    if not job:
        return jsonify({
            "error": True,
            "message": "Job not found"
        }), 404

    # Job must currently be in progress
    if job.status != "in_progress":
        return jsonify({
            "error": True,
            "message": "Only jobs that are in progress can be marked as complete"
        }), 400

    # Find the accepted bid
    accepted_bid = Bid.query.filter_by(
        job_id=job.id,
        status="accepted"
    ).first()

    if not accepted_bid:
        return jsonify({
            "error": True,
            "message": "No accepted vendor found for this job"
        }), 400

    # Only the accepted vendor can complete the job
    if accepted_bid.vendor_id != user_id:
        return jsonify({
            "error": True,
            "message": "Only the accepted vendor can mark this job as complete"
        }), 403

    job.status = "awaiting_approval"

    db.session.commit()

    return jsonify({
        "error": False,
        "message": "Job marked as complete and is awaiting client approval",
        "data": {
            "job_id": job.id,
            "status": job.status
        }
    }), 200


@jobs.route("/jobs/<int:job_id>/approve", methods=["PUT"])
@jwt_required()
def approve_job(job_id):

    user_id = int(get_jwt_identity())

    job = Job.query.get(job_id)

    if not job:
        return jsonify({
            "error": True,
            "message": "Job not found"
        }), 404

    # Only awaiting-approval jobs can be approved
    if job.status != "awaiting_approval":
        return jsonify({
            "error": True,
            "message": "This job is not awaiting approval"
        }), 400

    # Only the client who created the job can approve it
    if job.client_id != user_id:
        return jsonify({
            "error": True,
            "message": "Only the client who created this job can approve it"
        }), 403

    job.status = "completed"

    db.session.commit()

    return jsonify({
        "error": False,
        "message": "Job approved successfully",
        "data": {
            "job_id": job.id,
            "status": job.status
        }
    }), 200
    
@jobs.route("/jobs/my-vendor-jobs", methods=["GET"])
@jwt_required()
def get_my_vendor_jobs():

    user_id = int(get_jwt_identity())

    # Find all jobs where this vendor has an accepted bid
    accepted_bids = Bid.query.filter_by(
        vendor_id=user_id,
        status="accepted"
    ).all()

    jobs_data = []

    for bid in accepted_bids:

        job = Job.query.get(bid.job_id)

        if not job:
            continue

        jobs_data.append({
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "scope": job.scope,
            "duration": job.duration,
            "experience_level": job.experience_level,
            "budget": float(job.budget),
            "status": job.status,
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
    
@jobs.route("/jobs/my-jobs/active", methods=["GET"])
@jwt_required()
def get_my_active_jobs():

    user_id = int(get_jwt_identity())

    jobs = Job.query.filter(
        Job.client_id == user_id,
        Job.status.in_(["in_progress", "awaiting_approval"])
    ).order_by(Job.created_at.desc()).all()

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
    
@jobs.route("/jobs/my-jobs/completed", methods=["GET"])
@jwt_required()
def get_my_completed_jobs():

    user_id = int(get_jwt_identity())

    jobs = Job.query.filter(
        Job.client_id == user_id,
        Job.status == "completed"
    ).order_by(Job.created_at.desc()).all()

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