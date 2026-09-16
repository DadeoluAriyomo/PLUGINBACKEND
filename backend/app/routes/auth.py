from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from app import db
from app.models import User
from app.models import Category
import re


auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    # Check if request contains JSON data
    if not data:
        return jsonify({
            "error": True,
            "message": "Request body is required",
            "data": None
        }), 400

    # Get data from request
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")
    phone = data.get("phone")

    # Check required fields
    if not first_name or not last_name or not email or not password or not role:
        return jsonify({
            "error": True,
            "message": "First name, last name, email, password and role are required",
            "data": None
        }), 400

    # Remove unnecessary spaces
    email = email.strip().lower()

    # Basic email validation
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    if not re.match(email_pattern, email):
        return jsonify({
            "error": True,
            "message": "Invalid email address",
            "data": None
        }), 400

    # Check if email already exists
    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({
            "error": True,
            "message": "Email already registered",
            "data": None
        }), 409

    # Hash password
    password_hash = generate_password_hash(password)

    # Create user
    new_user = User(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        email=email,
        password_hash=password_hash,
        role=role,
        phone=phone
    )

    # Save user
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "error": False,
        "message": "Registration successful",
        "data": {
            "id": new_user.id,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "email": new_user.email,
            "role": new_user.role,
            "phone": new_user.phone,
            "status": new_user.status
        }
    }), 201
    
@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "error": True,
            "message": "Email and password are required",
            "data": None
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "error": True,
            "message": "Invalid email or password",
            "data": None
        }), 401

    if not check_password_hash(user.password_hash, password):
        return jsonify({
            "error": True,
            "message": "Invalid email or password",
            "data": None
        }), 401

    if user.status != "active":
        return jsonify({
            "error": True,
            "message": "Your account is not active",
            "data": None
        }), 403

    token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role
        }
    )

    return jsonify({
        "error": False,
        "message": "Login successful",
        "data": {
            "token": token,
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "role": user.role,
                "status": user.status
            }
        }
    }), 200
    

        
    