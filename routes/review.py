from flask import Blueprint, request, Response
import database.review as review_service
from middleware.auth import validate_token
import json

review_bp = Blueprint("review", __name__)


@review_bp.route("/", methods=["POST"])
@validate_token
def create_review(user_id):

    data = json.loads(request.data)

    # Create review
    try:

        review = review_service.create_review(
            {
                "user_id": user_id,
                "exp_id": data["exp_id"],
                "rating": data["rating"],
                "comment": data["comment"],
            }
        )
        return Response(json.dumps({"review": review}), status=200)

    # Handle exception
    except Exception as message:

        return Response(json.dumps({"message": str(message)}), status=400)


@review_bp.route("/<review_id>", methods=["POST"])
@validate_token
def update_review(user_id, review_id):

    data = json.loads(request.data)

    # Update review
    try:

        review = review_service.update_review(
            {
                "review_id": review_id,
                "rating": data["rating"],
                "comment": data["comment"],
            }
        )
        return Response(json.dumps({"review": review}), status=200)

    # Handle exception
    except Exception as message:

        return Response(json.dumps({"message": str(message)}), status=400)


@review_bp.route("/<review_id>", methods=["DELETE"])
@validate_token
def delete_review(user_id, review_id):

    # Delete review
    try:

        review_service.delete_review(review_id)
        return Response(json.dumps({"review_id": review_id}), status=200)

    # Handle exception
    except Exception as message:

        return Response(json.dumps({"message": str(message)}), status=400)
