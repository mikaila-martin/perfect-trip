from flask import Blueprint, abort, request
from services.google import places_nearby
from database import *
import json
from routes import auth

experience_bp = Blueprint("experience", __name__)


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


def pack_keywords(keywords):
    keywords_list = []
    for tup in keywords:
        keywords_list.append(tup[0])
    return keywords_list


def pack_experience(experience_data, user_data, review_data, keywords):
    review_list = pack_reviews(review_data)
    keywords_list = pack_keywords(keywords)
    packed_experience = {
        "experienceId": experience_data[0],
        "name": experience_data[2],
        "description": experience_data[3],
        "keywords": keywords_list,
        "coordinates": {
            "lat": float(experience_data[4]),
            "lon": float(experience_data[5]),
        },
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


@experience_bp.route("/", methods=["GET"])
@experience_bp.route("/<exp_id>", methods=["GET"])
@experience_bp.route("/<exp_id>/<rev_id>", methods=["GET"])
def experience_getter(exp_id=None, rev_id=None):
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
            experience_data, user_data, review_data, keywords = (
                response[0],
                response[1],
                response[2],
                response[3],
            )
            return json.dumps(
                pack_experience(experience_data, user_data, review_data, keywords)
            )
    else:
        abort(400)


@experience_bp.route("/", methods=["POST", "PATCH", "DELETE"])
@experience_bp.route("/<exp_id>", methods=["POST", "PATCH", "DELETE"])
@experience_bp.route("/<exp_id>/<rev_id>", methods=["POST", "PATCH", "DELETE"])
@auth.token_required
def experience(token_id, exp_id=None, rev_id=None):
    if request.method == "POST":
        if exp_id is not None:
            review_data = json.loads(request.data)
            if review_data["userId"] is None:
                abort(401)
            if review_data["userId"] != int(token_id):
                abort(403)
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
            if experience_data["userId"] is None:
                abort(401)
            if experience_data["userId"] != int(token_id):
                abort(403)
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
            return json.dumps(
                pack_experience(response[0], response[1], response[2], response[3])
            )
    elif request.method == "PATCH":
        if exp_id is not None and rev_id is not None:
            review_data = json.loads(request.data)
            if review_data["userId"] is None:
                abort(401)
            if review_data["userId"] != int(token_id):
                abort(403)
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
            if experience_data["userId"] is None:
                abort(401)
            if experience_data["userId"] != int(token_id):
                abort(403)
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
            return json.dumps(
                pack_experience(response[0], response[1], response[2], response[3])
            )
        else:
            abort(400)
    elif request.method == "DELETE":
        if rev_id is not None:
            response = delete_review(rev_id, token_id)
            if response == 1:
                abort(404)
            elif response == 2:
                abort(403)
            return "Successfully Deleted"
        elif exp_id is not None:
            response = delete_experience(exp_id, token_id)
            if response == 1:
                abort(404)
            elif response == 2:
                abort(403)
            return "Successfully Deleted"
        else:
            abort(400)


@experience_bp.route("/user_experiences/<user_id>", methods=["GET"])
@auth.token_required
def experiences_by_user(token_id, user_id):
    if user_id is not None:
        if token_id != user_id:
            abort(403)
        exp_array = []
        response = get_experiences_by_user(user_id)
        for exp in response:
            packed_exp = pack_experience(exp[0], exp[1], exp[2], exp[3])
            exp_array.append(packed_exp)
        return json.dumps({"experiences": exp_array})
    else:
        return abort(400)


@experience_bp.route("/map", methods=["GET"])
def experiences_by_location():
    north = int(request.args["ne"].split(",")[0])
    east = int(request.args["ne"].split(",")[1])
    south = int(request.args["sw"].split(",")[0])
    west = int(request.args["sw"].split(",")[1])
    exp_array = []
    response = get_experiences_by_location(north, south, east, west)
    for exp in response:
        packed_exp = pack_experience(exp[0], exp[1], exp[2], exp[3])
        exp_array.append(packed_exp)
    return json.dumps({"experiences": exp_array})


@experience_bp.route("/search", methods=["GET"])
def search():

    exp_array = []

    # Extract keywords
    keywords = request.args.get("keywords")
    keywords = [] if keywords == "" else keywords.split(",")

    # Extract map center
    c_lat = float(request.args.get("c_lat"))
    c_lng = float(request.args.get("c_lng"))

    # Get experiences from Google
    places = places_nearby(c_lat, c_lng, keywords)

    for place in places:
        exp_array.append(place)

    # Extract map bounding box
    ne_lat = float(request.args.get("ne_lat"))
    ne_lng = float(request.args.get("ne_lng"))
    sw_lat = float(request.args.get("sw_lat"))
    sw_lng = float(request.args.get("sw_lng"))

    # Get experiences from database
    response = search_experiences(ne_lat, sw_lat, ne_lng, sw_lng, keywords)

    for exp in response:
        packed_exp = pack_experience(exp[0], exp[1], exp[2], exp[3])
        exp_array.append(packed_exp)

    return json.dumps({"experiences": exp_array})


@experience_bp.route("/keywords", methods=["GET"])
def keywords():
    keyword_list = []
    response = get_keywords()
    for keyword_tup in response:
        keyword_list.append(keyword_tup[0])
    return json.dumps({"keywords": keyword_list})
