from flask import Blueprint, abort, request
import database.review as review_entity
from middleware.auth import validate_token
import json

review_bp = Blueprint("review", __name__)


@review_bp.route("/", methods=["POST"])
@validate_token
def create_review(user_id):
    data = json.loads(request.data)

    # Create review
    response = review_entity.create_review(
        user_id,
        data["exp_id"],
        data["rating"],
        data["comment"],
    )

    if response == 1:
        abort(403)

    return json.dumps(pack_reviews(response))


@review_bp.route("/<rev_id>", methods=["POST"])
@validate_token
def update_review(user_id, rev_id):
    data = json.loads(request.data)

    # Update review
    response = review_entity.update_review(
        rev_id,
        data["rating"],
        data["comment"],
    )

    if response == 1:
        abort(404)

    if response == 2:
        abort(403)

    return json.dumps(pack_reviews(response))


@review_bp.route("/<rev_id>", methods=["DELETE"])
@validate_token
def delete_review(user_id, rev_id):

    # Delete review
    response = review_entity.delete_review(rev_id)

    if response == 1:
        abort(404)

    if response == 2:
        abort(403)

    return "Successfully Deleted"
