from flask import request
from config import jwt_secret_key
import database.user as user_entity
from functools import wraps
import jwt


def validate_token(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        # Get token from authorization header
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            token = auth_header.split()[1]

        # Return error message on missing token
        if not token:
            return "token is missing", 400

        # Attempt to decode token and fetch user from database
        try:
            payload = jwt.decode(token, jwt_secret_key, algorithms=["HS256"])
            user = user_entity.get_by_id(payload["userId"])

        # Return error message on invalid token
        except:
            return "token is invalid", 400

        # Pass user id to next route
        user_id = user["user_id"]
        return f(user_id, *args, **kwargs)

    return decorator
