from flask import Blueprint, request, Response
import database.review as review_entity
from middleware.auth import validate_token
import database.experience as experience_entity
from util import pack_reviews
import json

review_bp = Blueprint("review", __name__)


@review_bp.route("/<rev_id>", methods=["GET"])
def get_a_review(rev_id):
    try:
        review = review_entity.get_review(rev_id)
        response = experience_entity.get_experience_by_id(review["exp_id"])
        return Response(json.dumps({"experience": response}))
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@review_bp.route("/", methods=["POST"])
@validate_token
def create_review(user_id):
    try:
        data = json.loads(request.data)

        # Create review
        review_entity.create_review(
            user_id,
            data["experienceId"],
            data["rating"],
            data["rev"],
        )

        # Get Experience
        experience = experience_entity.get_experience_by_id(data["experienceId"])
        return Response(json.dumps({"experience": experience}), status=200)

    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@review_bp.route("/<rev_id>", methods=["PATCH"])
@validate_token
def update_review(user_id, rev_id):
    try:
        data = json.loads(request.data)
        # Update review
        response = review_entity.update_review(
            user_id,
            rev_id,
            data["rating"],
            data["comment"],
        )

        return json.dumps(pack_reviews(response))
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@review_bp.route("/<rev_id>", methods=["DELETE"])
@validate_token
def delete_a_review(user_id, rev_id):
    try:
        # Delete review
        review_entity.delete_review(user_id, rev_id)
        return Response(json.dumps({"message": "Review Deleted"}), status=200)
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)
