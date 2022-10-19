from flask import abort, request
from database import *
from app import app
import hashlib
import json


def hash_password(password):
    password = password.encode()
    password_hash = hashlib.sha224(password)
    return password_hash.digest().hex()


@app.route("/auth/login", methods=["POST"])
def login():
    login_info = json.loads(request.data)
    username = login_info["username"]
    password = login_info["password"]
    password_hash = hash_password(password)
    login_response = login_user(username, password_hash)
    if login_response == 1:
        abort(403)
    else:
        return json.dumps(
            {
                "userId": login_response[0],
                "username": login_response[1],
                "avatar": login_response[2],
            }
        )


@app.route("/auth/register", methods=["POST"])
def register():
    registration_info = json.loads(request.data)
    username = registration_info["username"]
    password_a = registration_info["passwordA"]
    password_b = registration_info["passwordB"]
    email = registration_info["email"]
    if password_b != password_a:
        return "PASSWORD NOT EQUAL FLOPPA ERROR"
    else:
        password_hash = hash_password(password_b)
        registration_response = register_user(username, password_hash, email)
        if registration_response == 1:
            return "EMAIL IN USE FLOPPA ERROR"
        return json.dumps(
            {
                "userId": registration_response[0],
                "username": registration_response[1],
                "avatar": registration_response[2],
            }
        )
