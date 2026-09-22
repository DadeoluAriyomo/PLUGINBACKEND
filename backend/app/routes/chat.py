from flask import Blueprint, jsonify,request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from app import db
from app.models import User, Job, Bid, Conversation, Message


chat = Blueprint("chat", __name__)


@chat.route("/jobs/<int:job_id>/conversation", methods=["POST"])
@jwt_required()
def create_conversation(job_id):

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "error": True,
            "message": "User not found",
            "data": None
        }), 404

    job = Job.query.get(job_id)

    if not job:
        return jsonify({
            "error": True,
            "message": "Job not found",
            "data": None
        }), 404

    # Job must be in progress
    if job.status != "in_progress":
        return jsonify({
            "error": True,
            "message": "Chat is only available for jobs in progress",
            "data": None
        }), 400

    # Find accepted bid
    accepted_bid = Bid.query.filter_by(
        job_id=job.id,
        status="accepted"
    ).first()

    if not accepted_bid:
        return jsonify({
            "error": True,
            "message": "No accepted vendor found for this job",
            "data": None
        }), 400

    # Only the client or accepted vendor can access the conversation
    if user.id != job.client_id and user.id != accepted_bid.vendor_id:
        return jsonify({
            "error": True,
            "message": "You are not part of this job",
            "data": None
        }), 403

    # Check if conversation already exists
    conversation = Conversation.query.filter_by(
        job_id=job.id
    ).first()

    if conversation:
        return jsonify({
            "error": False,
            "message": "Conversation already exists",
            "data": {
                "id": conversation.id,
                "job_id": conversation.job_id,
                "client_id": conversation.client_id,
                "vendor_id": conversation.vendor_id,
                "created_at": conversation.created_at
            }
        }), 200

    # Create conversation
    conversation = Conversation(
        job_id=job.id,
        client_id=job.client_id,
        vendor_id=accepted_bid.vendor_id
    )

    db.session.add(conversation)
    db.session.commit()

    return jsonify({
        "error": False,
        "message": "Conversation created successfully",
        "data": {
            "id": conversation.id,
            "job_id": conversation.job_id,
            "client_id": conversation.client_id,
            "vendor_id": conversation.vendor_id,
            "created_at": conversation.created_at
        }
    }), 201
    
@chat.route("/conversations/<int:conversation_id>/messages", methods=["POST"])
@jwt_required()
def send_message(conversation_id):

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "error": True,
            "message": "User not found",
            "data": None
        }), 404

    conversation = Conversation.query.get(conversation_id)

    if not conversation:
        return jsonify({
            "error": True,
            "message": "Conversation not found",
            "data": None
        }), 404

    # Only the client and accepted vendor can send messages
    if user.id not in [
        conversation.client_id,
        conversation.vendor_id
    ]:
        return jsonify({
            "error": True,
            "message": "You are not part of this conversation",
            "data": None
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            "error": True,
            "message": "Request body is required",
            "data": None
        }), 400

    message_text = data.get("message")

    if not message_text or not message_text.strip():
        return jsonify({
            "error": True,
            "message": "Message is required",
            "data": None
        }), 400

    message = Message(
        conversation_id=conversation.id,
        sender_id=user.id,
        message=message_text.strip()
    )

    db.session.add(message)

    conversation.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "error": False,
        "message": "Message sent successfully",
        "data": {
            "id": message.id,
            "conversation_id": message.conversation_id,
            "sender_id": message.sender_id,
            "message": message.message,
            "is_read": message.is_read,
            "created_at": message.created_at
        }
    }), 201
    
@chat.route("/conversations/<int:conversation_id>/messages", methods=["GET"])
@jwt_required()
def get_messages(conversation_id):

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "error": True,
            "message": "User not found",
            "data": None
        }), 404

    conversation = Conversation.query.get(conversation_id)

    if not conversation:
        return jsonify({
            "error": True,
            "message": "Conversation not found",
            "data": None
        }), 404

    # Only conversation participants can see messages
    if user.id not in [
        conversation.client_id,
        conversation.vendor_id
    ]:
        return jsonify({
            "error": True,
            "message": "You are not part of this conversation",
            "data": None
        }), 403

    messages = Message.query.filter_by(
        conversation_id=conversation.id
    ).order_by(
        Message.created_at.asc()
    ).all()

    result = []

    for message in messages:
        result.append({
            "id": message.id,
            "conversation_id": message.conversation_id,
            "sender_id": message.sender_id,
            "message": message.message,
            "is_read": message.is_read,
            "created_at": message.created_at
        })

    return jsonify({
        "error": False,
        "message": "Messages retrieved successfully",
        "data": result
    }), 200