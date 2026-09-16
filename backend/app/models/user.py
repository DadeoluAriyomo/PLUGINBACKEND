from app import db
from datetime import datetime
from app.models.vendor_category import vendor_categories


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(100), nullable=False)

    last_name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False)

    phone = db.Column(db.String(20), nullable=True)

    profile_image = db.Column(db.String(255), nullable=True)

    status = db.Column(db.String(20), default="active", nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    categories = db.relationship(
    "Category",
    secondary=vendor_categories,
    backref=db.backref("vendors", lazy="dynamic")
)

    def __repr__(self):
        return f"<User {self.email}>"