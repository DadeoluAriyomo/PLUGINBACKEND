from app import db
from datetime import datetime


class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)

    job_id = db.Column(
        db.Integer,
        db.ForeignKey("jobs.id"),
        nullable=False,
        unique=True
    )

    client_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    vendor_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    job = db.relationship(
        "Job",
        backref=db.backref("conversation", uselist=False)
    )

    client = db.relationship(
        "User",
        foreign_keys=[client_id]
    )

    vendor = db.relationship(
        "User",
        foreign_keys=[vendor_id]
    )