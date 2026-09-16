from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.user import User
from app.models.category import Category


vendors = Blueprint("vendors", __name__)


@vendors.route("/vendors/categories", methods=["PUT"])
@jwt_required()
def update_vendor_categories():

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
            "message": "Only vendors can update categories",
            "data": None
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            "error": True,
            "message": "Request body is required",
            "data": None
        }), 400

    category_ids = data.get("category_ids")

    if not isinstance(category_ids, list):
        return jsonify({
            "error": True,
            "message": "category_ids must be an array",
            "data": None
        }), 400

    if len(category_ids) == 0:
        return jsonify({
            "error": True,
            "message": "At least one category is required",
            "data": None
        }), 400

    categories = Category.query.filter(
        Category.id.in_(category_ids)
    ).all()

    if len(categories) != len(set(category_ids)):
        return jsonify({
            "error": True,
            "message": "One or more categories were not found",
            "data": None
        }), 404

    # Replace the vendor's existing categories
    user.categories = categories

    db.session.commit()

    return jsonify({
        "error": False,
        "message": "Vendor categories updated successfully",
        "data": [
            {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "image": category.image
            }
            for category in user.categories
        ]
    }), 200

@vendors.route("/vendors/categories", methods=["GET"])
@jwt_required()
def get_vendor_categories():

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
            "message": "Only vendors can access this endpoint",
            "data": None
        }), 403

    categories_data = []

    for category in user.categories:
        categories_data.append({
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "image": category.image
        })

    return jsonify({
        "error": False,
        "message": "Vendor categories retrieved successfully",
        "data": categories_data
    }), 200