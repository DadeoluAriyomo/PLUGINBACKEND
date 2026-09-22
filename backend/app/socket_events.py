from datetime import datetime
from flask_socketio import emit, join_room
from flask_jwt_extended import decode_token

from app import socketio, db
from app.models import User, Conversation, Message


@socketio.on("join_conversation")
def handle_join_conversation(data):

    token = data.get("token")
    conversation_id = data.get("conversation_id")

    if not token or not conversation_id:
        emit("error", {
            "message": "Token and conversation_id are required"
        })
        return

    try:
        decoded = decode_token(token)
        user_id = int(decoded["sub"])
    except Exception:
        emit("error", {
            "message": "Invalid or expired token"
        })
        return

    user = User.query.get(user_id)

    if not user:
        emit("error", {
            "message": "User not found"
        })
        return

    conversation = Conversation.query.get(conversation_id)

    if not conversation:
        emit("error", {
            "message": "Conversation not found"
        })
        return

    # Only the client and vendor can join
    if user.id not in [
        conversation.client_id,
        conversation.vendor_id
    ]:
        emit("error", {
            "message": "You are not part of this conversation"
        })
        return

    room = f"conversation_{conversation.id}"

    join_room(room)

    emit("joined_conversation", {
        "message": "Joined conversation successfully",
        "conversation_id": conversation.id
    })


@socketio.on("send_message")
def handle_send_message(data):

    token = data.get("token")
    conversation_id = data.get("conversation_id")
    message_text = data.get("message")

    if not token or not conversation_id or not message_text:
        emit("error", {
            "message": "Token, conversation_id and message are required"
        })
        return

    try:
        decoded = decode_token(token)
        user_id = int(decoded["sub"])
    except Exception:
        emit("error", {
            "message": "Invalid or expired token"
        })
        return

    user = User.query.get(user_id)

    if not user:
        emit("error", {
            "message": "User not found"
        })
        return

    conversation = Conversation.query.get(conversation_id)

    if not conversation:
        emit("error", {
            "message": "Conversation not found"
        })
        return

    # Only participants can send messages
    if user.id not in [
        conversation.client_id,
        conversation.vendor_id
    ]:
        emit("error", {
            "message": "You are not part of this conversation"
        })
        return

    message_text = message_text.strip()

    if not message_text:
        emit("error", {
            "message": "Message cannot be empty"
        })
        return

    # Save message
    message = Message(
        conversation_id=conversation.id,
        sender_id=user.id,
        message=message_text
    )

    db.session.add(message)

    conversation.updated_at = datetime.utcnow()

    db.session.commit()

    room = f"conversation_{conversation.id}"

    # Send message to everyone in the conversation
    emit(
        "new_message",
        {
            "id": message.id,
            "conversation_id": message.conversation_id,
            "sender_id": message.sender_id,
            "message": message.message,
            "is_read": message.is_read,
            "created_at": message.created_at.isoformat()
        },
        to=room
    )