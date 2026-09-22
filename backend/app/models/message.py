from app import db
from datetime import datetime


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)

    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey("conversations.id"),
        nullable=False
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    is_read = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    conversation = db.relationship(
        "Conversation",
        backref=db.backref("messages", lazy=True)
    )

    sender = db.relationship(
        "User",
        backref=db.backref("sent_messages", lazy=True)
    )