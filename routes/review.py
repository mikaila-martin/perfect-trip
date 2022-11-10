from flask import Blueprint, request, Response
import database.review as review_entity
from middleware.auth import validate_token
from util import pack_reviews
import json

review_bp = Blueprint("review", __name__)


@review_bp.route("/<rev_id>", methods=["GET"])
def get_a_review(rev_id):
    try:
        response = review_entity.get_review(rev_id)
        return json.dumps(pack_reviews(response)[0])
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@review_bp.route("/", methods=["POST"])
@validate_token
def create_review(user_id):
    try:
        data = json.loads(request.data)

        # Create review
        response = review_entity.create_review(
            user_id,
            data["exp_id"],
            data["rating"],
            data["comment"],
        )

        return json.dumps(pack_reviews(response))
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
def delete_review(user_id, rev_id):
    try:
        # Delete review
        review_entity.delete_review(user_id, rev_id)
        Response(json.dumps({"message": "Review Deleted"}), status=200)
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)

