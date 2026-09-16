from app import db


vendor_categories = db.Table(
    "vendor_categories",

    db.Column(
        "vendor_id",
        db.Integer,
        db.ForeignKey("users.id"),
        primary_key=True
    ),

    db.Column(
        "category_id",
        db.Integer,
        db.ForeignKey("categories.id"),
        primary_key=True
    )
)