from flask import Blueprint, json, request, Response
from middleware.auth import validate_token
from database.user import *
from routes.auth import generate_token, hash_password
import services.aws as aws


user_bp = Blueprint("user", __name__)


@user_bp.route("/update/user", methods=["POST"])
@validate_token
def update_username(user_id):
    try:
        username = json.loads(request.data)["username"]
        user = update_username_db(user_id, username)
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
            return Response(json.dumps({"message": "Passwords not Equal."}), status=400)
        update_password_db(user_id, hash_password(data["passwordA"]))
        return Response(json.dumps({"message": "Password updated."}), status=200)
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@user_bp.route("/delete", methods=["POST"])
@validate_token
def delete_account(user_id):
    try:
        data = json.loads(request.data)
        pass_hash = hash_password(data["passwordD"])
        check_password(user_id, pass_hash)
        delete_account_db(user_id)
        return Response(json.dumps({"message": "Account Deleted"}), status=200)
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@user_bp.route("/update/avatar", methods=["POST"])
@validate_token
def update_avatar(user_id):
    try:
        avatar = json.loads(request.data)["avatar"]
        past_avatar = get_avatar_by_user(user_id)
        if past_avatar:
            avatar_key = past_avatar.split("/")[-1]
            aws.delete_image(avatar_key)
        image_key = aws.upload_image(avatar[0])
        user = update_avatar_db(user_id, image_key)
        token = generate_token(user["user_id"], user["username"], user["avatar"])
        return Response(json.dumps({"token": token}), status=200)
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)
