from app import db
from datetime import datetime


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)

    client_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    title = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    skills_required = db.Column(
        db.JSON,
        nullable=False
    )

    scope = db.Column(
        db.Text,
        nullable=False
    )

    duration = db.Column(
        db.String(100),
        nullable=False
    )

    experience_level = db.Column(
        db.String(50),
        nullable=False
    )

    budget = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    status = db.Column(
        db.String(50),
        default="open",
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

    # Relationships
    client = db.relationship(
        "User",
        backref=db.backref("jobs", lazy=True)
    )

    category = db.relationship(
        "Category",
        backref=db.backref("jobs", lazy=True)
    )