from flask import Blueprint, jsonify
from app.models.category import Category

categories = Blueprint("categories", __name__)

@categories.route("/categories", methods=["GET"])
def get_categories():
    all_categories = Category.query.order_by(Category.id.asc()).all()
    categories_data=[]
    
    for category in all_categories:
        categories_data.append({
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "image": category.image
        })

    return jsonify({
        "error": False,
        "message": "Categories fetched successfully",
        "data": categories_data
    }), 200