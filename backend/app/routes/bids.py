from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.user import User
from app.models.job import Job
from app.models.bid import Bid


bids = Blueprint("bids", __name__)


@bids.route("/jobs/<int:job_id>/bids", methods=["POST"])
@jwt_required()
def submit_bid(job_id):

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "error": True,
            "message": "User not found",
            "data": None
        }), 404

    if user.role != "vendor":
        return jsonify({
            "error": True,
            "message": "Only vendors can submit bids",
            "data": None
        }), 403

    job = Job.query.get(job_id)

    if not job:
        return jsonify({
            "error": True,
            "message": "Job not found",
            "data": None
        }), 404

    if job.status != "open":
        return jsonify({
            "error": True,
            "message": "This job is no longer accepting bids",
            "data": None
        }), 400

    # Make sure vendor belongs to the job's category
    vendor_category_ids = [
        category.id for category in user.categories
    ]

    if job.category_id not in vendor_category_ids:
        return jsonify({
            "error": True,
            "message": "You cannot bid on jobs outside your service categories",
            "data": None
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            "error": True,
            "message": "Request body is required",
            "data": None
        }), 400

    amount = data.get("amount")
    proposal = data.get("proposal")
    estimated_duration = data.get("estimated_duration")

    if amount is None:
        return jsonify({
            "error": True,
            "message": "Bid amount is required",
            "data": None
        }), 400

    if not proposal:
        return jsonify({
            "error": True,
            "message": "Proposal is required",
            "data": None
        }), 400

    if not estimated_duration:
        return jsonify({
            "error": True,
            "message": "Estimated duration is required",
            "data": None
        }), 400

    try:
        amount = float(amount)

        if amount <= 0:
            return jsonify({
                "error": True,
                "message": "Bid amount must be greater than zero",
                "data": None
            }), 400

    except (ValueError, TypeError):
        return jsonify({
            "error": True,
            "message": "Bid amount must be a valid number",
            "data": None
        }), 400

    # Prevent the same vendor from bidding twice
    existing_bid = Bid.query.filter_by(
        job_id=job.id,
        vendor_id=user.id
    ).first()

    if existing_bid:
        return jsonify({
            "error": True,
            "message": "You have already submitted a bid for this job",
            "data": None
        }), 409

    new_bid = Bid(
        job_id=job.id,
        vendor_id=user.id,
        amount=amount,
        proposal=proposal,
        estimated_duration=estimated_duration,
        status="pending"
    )

    db.session.add(new_bid)
    db.session.commit()

    return jsonify({
        "error": False,
        "message": "Bid submitted successfully",
        "data": {
            "id": new_bid.id,
            "job_id": new_bid.job_id,
            "vendor_id": new_bid.vendor_id,
            "amount": float(new_bid.amount),
            "proposal": new_bid.proposal,
            "estimated_duration": new_bid.estimated_duration,
            "status": new_bid.status,
            "created_at": new_bid.created_at.isoformat()
        }
    }), 201
    
@bids.route("/jobs/<int:job_id>/bids", methods=["GET"])
@jwt_required()
def get_job_bids(job_id):

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "error": True,
            "message": "User not found",
            "data": None
        }), 404

    # Only clients can view bids
    if user.role != "client":
        return jsonify({
            "error": True,
            "message": "Only clients can view bids",
            "data": None
        }), 403

    # Find the job
    job = Job.query.get(job_id)

    if not job:
        return jsonify({
            "error": True,
            "message": "Job not found",
            "data": None
        }), 404

    # Make sure this job belongs to the logged-in client
    if job.client_id != user.id:
        return jsonify({
            "error": True,
            "message": "You can only view bids for your own jobs",
            "data": None
        }), 403

    # Get all bids for this job
    bids = Bid.query.filter_by(job_id=job.id)\
        .order_by(Bid.created_at.desc())\
        .all()

    bids_data = []

    for bid in bids:

        bids_data.append({
            "id": bid.id,
            "job_id": bid.job_id,
            "vendor_id": bid.vendor_id,

            "vendor": {
                "id": bid.vendor.id,
                "first_name": bid.vendor.first_name,
                "last_name": bid.vendor.last_name,
                "email": bid.vendor.email
            },

            "amount": float(bid.amount),
            "proposal": bid.proposal,
            "estimated_duration": bid.estimated_duration,
            "status": bid.status,
            "created_at": bid.created_at.isoformat(),
            "updated_at": bid.updated_at.isoformat()
                if bid.updated_at else None
        })

    return jsonify({
        "error": False,
        "message": "Bids retrieved successfully",
        "data": bids_data,
        "count": len(bids_data)
    }), 200
    
@bids.route("/bids/<int:bid_id>/accept", methods=["PUT"])
@jwt_required()
def accept_bid(bid_id):

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "error": True,
            "message": "User not found",
            "data": None
        }), 404

    # Only clients can accept bids
    if user.role != "client":
        return jsonify({
            "error": True,
            "message": "Only clients can accept bids",
            "data": None
        }), 403

    # Find the bid
    bid = Bid.query.get(bid_id)

    if not bid:
        return jsonify({
            "error": True,
            "message": "Bid not found",
            "data": None
        }), 404

    # Get the job associated with the bid
    job = Job.query.get(bid.job_id)

    if not job:
        return jsonify({
            "error": True,
            "message": "Job not found",
            "data": None
        }), 404

    # Make sure this job belongs to the logged-in client
    if job.client_id != user.id:
        return jsonify({
            "error": True,
            "message": "You can only accept bids for your own jobs",
            "data": None
        }), 403

    # Job must still be open
    if job.status != "open":
        return jsonify({
            "error": True,
            "message": "This job is no longer open for bids",
            "data": None
        }), 400

    # Bid must still be pending
    if bid.status != "pending":
        return jsonify({
            "error": True,
            "message": "This bid is no longer available",
            "data": None
        }), 400

    # Accept selected bid
    bid.status = "accepted"

    # Reject all other bids for this job
    other_bids = Bid.query.filter(
        Bid.job_id == job.id,
        Bid.id != bid.id
    ).all()

    for other_bid in other_bids:
        other_bid.status = "rejected"

    # Move job to in_progress
    job.status = "in_progress"

    db.session.commit()

    return jsonify({
        "error": False,
        "message": "Bid accepted successfully",
        "data": {
            "bid_id": bid.id,
            "job_id": job.id,
            "vendor_id": bid.vendor_id,
            "bid_status": bid.status,
            "job_status": job.status
        }
    }), 200