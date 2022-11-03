from flask import Blueprint, abort, request
from services.google import places_nearby
from database import *
import json

experience_bp = Blueprint("experience", __name__)


@experience_bp.route("/search", methods=["GET"])
def search():

    # Keywords
    keywords = request.args.get("keywords")
    keywords = [] if keywords == "" else keywords.split(",")

    # Map center
    c_lat = request.args.get("c_lat")
    c_lng = request.args.get("c_lng")

    # Get nearby places
    places = places_nearby(c_lat, c_lng, keywords)

    # Map bounding box
    ne_lat = request.args.get("ne_lat")
    ne_lng = request.args.get("ne_lng")
    sw_lat = request.args.get("sw_lat")
    sw_lng = request.args.get("sw_lng")

    # TODO: Get all experiences that fall within bounding box

    return places


def pack_reviews(review_data):
    review_list = []
    for tup in review_data:
        review = {
            "reviewId": tup[0],
            "rating": tup[1],
            "comment": tup[2],
            "user": {"userId": tup[3], "username": tup[4], "avatar": tup[5]},
        }
        review_list.append(review)
    return review_list


def pack_experience(experience_data, user_data, review_data):
    review_list = pack_reviews(review_data)
    packed_experience = {
        "experienceId": experience_data[0],
        "name": experience_data[2],
        "description": experience_data[3],
        "keywords": "array[string]",
        "coordinates": {"lat": experience_data[4], "lon": experience_data[5]},
        "dates": {"start": str(experience_data[6]), "end": str(experience_data[7])},
        "images": experience_data[8],
        "country": experience_data[9],
        "creator": {
            "userId": user_data[0],
            "username": user_data[1],
            "avatar": user_data[2],
        },
        "reviews": review_list,
    }
    return packed_experience


@experience_bp.route("/", methods=["GET", "POST", "PATCH", "DELETE"])
@experience_bp.route("/<exp_id>", methods=["GET", "POST", "PATCH", "DELETE"])
@experience_bp.route("/<exp_id>/<rev_id>", methods=["GET", "POST", "PATCH", "DELETE"])
def experience(exp_id=None, rev_id=None):
    if request.method == "GET":
        if exp_id is not None and rev_id is not None:
            response = get_review(rev_id)
            if response == 1:
                abort(404)
            else:
                return json.dumps(pack_reviews(response)[0])
        elif exp_id is not None and rev_id is None:
            response = get_experience(exp_id)
            if response == 1:
                abort(404)
            else:
                experience_data, user_data, review_data = (
                    response[0],
                    response[1],
                    response[2],
                )
                return json.dumps(
                    pack_experience(experience_data, user_data, review_data)
                )
        else:
            abort(400)
    elif request.method == "POST":
        if exp_id is not None:
            review_data = json.loads(request.data)
            response = make_review(
                review_data["userId"],
                exp_id,
                review_data["rating"],
                review_data["comment"],
            )
            if response == 1:
                abort(403)
            return json.dumps(pack_reviews(response))
        else:
            experience_data = json.loads(request.data)
            response = make_experience(
                user_id=experience_data["userId"],
                name=experience_data["name"],
                pictures=experience_data["images"],
                description=experience_data["description"],
                coords=experience_data["coordinates"],
                keywords=experience_data["keywords"],
                country=experience_data["country"],
                start=experience_data["dates"]["start"],
                end=experience_data["dates"]["end"],
            )
            if response == 2:
                abort(403)
            return json.dumps(pack_experience(response[0], response[1], response[2]))
    elif request.method == "PATCH":
        if exp_id is not None and rev_id is not None:
            review_data = json.loads(request.data)
            response = update_review(
                review_data["userId"],
                rev_id,
                review_data["rating"],
                review_data["comment"],
            )
            if response == 1:
                abort(404)
            if response == 2:
                abort(403)
            return json.dumps(pack_reviews(response))
        elif exp_id is not None:
            experience_data = json.loads(request.data)
            response = update_experience(
                exp_id=exp_id,
                user_id=experience_data["userId"],
                name=experience_data["name"],
                pictures=experience_data["images"],
                description=experience_data["description"],
                coords=experience_data["coordinates"],
                keywords=experience_data["keywords"],
                country=experience_data["country"],
                start=experience_data["dates"]["start"],
                end=experience_data["dates"]["end"],
            )
            if response == 1:
                abort(404)
            if response == 2:
                abort(403)
            return json.dumps(pack_experience(response[0], response[1], response[2]))
        else:
            abort(400)
    elif request.method == "DELETE":
        if exp_id is not None and rev_id is not None:
            response = delete_review(rev_id)
            if response == 1:
                abort(404)
            return
        elif exp_id is not None:
            response = delete_experience(exp_id)
            if response == 1:
                abort(404)
            return
        else:
            abort(400)


@experience_bp.route("/<user_id>", methods=["GET"])
def get_experiences_by_user(user_id):
    if user_id is not None:
        return get_experiences_by_user(user_id)
    else:
        return abort(400)
