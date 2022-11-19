from flask import Blueprint, json, request, Response
from middleware.auth import validate_token
from database.user import *
from routes.auth import generate_token, hash_password


user_bp = Blueprint("user", __name__)


@user_bp.route("/update/user", methods=["POST"])
@validate_token
def update_avatar(user_id):
    try:
        username = json.loads(request.data)["username"]
        user = update_username(user_id, username)
        token = generate_token(user["user_id"], user["username"], user["avatar"])

        return Response(json.dumps({"token": token}), status=200)
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@user_bp.route("/update/pass", methods=["POST"])
@validate_token
def update_password(user_id):
    try:
        data = json.loads(request.data)
        pass_hash = hash_password(data["password"])
        check_password(user_id, pass_hash)
        if data["passwordA"] != data["passwordB"]:
            return Response(json.dumps({"message": "Passwords not equal."}), status=400)
        update_password_db(user_id, hash_password(data["passwordA"]))
        return Response(json.dumps({"message": "Password updated"}), status=200)
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)
