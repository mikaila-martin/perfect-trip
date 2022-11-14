from flask import Blueprint, request, Response
from config import jwt_secret_key
import database.auth as auth_service
import hashlib
import json
import jwt


auth_bp = Blueprint("auth", __name__)

# Code for jwt authentication from
# https://www.bacancytechnology.com/blog/flask-jwt-authentication
# 10/29/2022


def hash_password(password):
    password = password.encode()
    password_hash = hashlib.sha224(password)
    return password_hash.digest().hex()


def generate_token(user_id, username, avatar):
    payload = {
        "userId": user_id,
        "username": username,
        "avatar": avatar,
    }

    token = jwt.encode(
        payload,
        jwt_secret_key,
        "HS256",
    )

    return token


@auth_bp.route("/register", methods=["POST"])
def register():
    credentials = json.loads(request.data)

    # Extract credentials
    username = credentials["username"]
    password_a = credentials["passwordA"]
    password_b = credentials["passwordB"]
    email = credentials["email"]

    # Handle password mismatch
    if password_b != password_a:

        return Response(json.dumps({"message": "Passwords not equal"}), status=400)

    # Generate password hash
    password_hash = hash_password(password_b)

    # Login user and generate JWT
    try:

        user = auth_service.register_user(email, username, password_hash)
        token = generate_token(user["user_id"], user["username"], user["avatar"])

        return Response(json.dumps({"token": token}), status=200)

    # Handle exception
    except Exception as message:

        return Response(json.dumps({"message": str(message)}), status=400)


@auth_bp.route("/login", methods=["POST"])
def login():
    credentials = json.loads(request.data)

    # Extract credentials
    email = credentials["email"]
    password = credentials["password"]

    # Generate password hash
    password_hash = hash_password(password)

    # Login user and generate JWT
    try:

        user = auth_service.login_user(email, password_hash)
        token = generate_token(user["user_id"], user["username"], user["avatar"])

        return Response(json.dumps({"token": token}), status=200)

    # Handle exception
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)
