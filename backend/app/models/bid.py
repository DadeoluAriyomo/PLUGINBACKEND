from app import db
from datetime import datetime


class Bid(db.Model):
    __tablename__ = "bids"

    id = db.Column(db.Integer, primary_key=True)

    job_id = db.Column(
        db.Integer,
        db.ForeignKey("jobs.id"),
        nullable=False
    )

    vendor_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    amount = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    proposal = db.Column(
        db.Text,
        nullable=False
    )

    estimated_duration = db.Column(
        db.String(100),
        nullable=False
    )

    status = db.Column(
        db.String(50),
        default="pending",
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
        backref=db.backref("bids", lazy=True)
    )

    vendor = db.relationship(
        "User",
        backref=db.backref("bids", lazy=True)
    )