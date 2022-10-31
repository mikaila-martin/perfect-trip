from flask import Blueprint, abort, request
from middleware.auth import validate_token
import database.experience as experience_entity
import database.trip as trip_entity
import json
from routes import auth

trip_bp = Blueprint("trip", __name__)


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


def get_and_pack_trip(trip_id):
    itin_data, exp_data, user_data = trip_entity.get_trip(trip_id)
    experiences_table = []
    for experience in exp_data:
        exp_info = experience_entity.get_experience(experience[0])
        packed_experience = pack_experience(
            exp_info[0], exp_info[1], exp_info[2], exp_info[3]
        )
        experiences_table.append(
            {
                "experience": packed_experience,
                "date": str(experience[1]),
                "time": str(experience[2]),
            }
        )
    user_table = []
    for user in user_data:
        user_table.append({"userId": user[0], "username": user[1], "avatar": user[2]})
    packed_trip = {
        "tripID": itin_data[0][0],
        "name": itin_data[0][1],
        "startDate": str(itin_data[0][2]),
        "endDate": str(itin_data[0][3]),
        "experiences": experiences_table,
        "members": user_table,
    }
    return packed_trip


@trip_bp.route("/", methods=["GET", "POST", "PATCH", "DELETE"])
@trip_bp.route("/<trip_id>", methods=["GET", "POST", "PATCH", "DELETE"])
@validate_token
def trip(token_id, trip_id=None):
    if request.method == "GET":
        if trip_id is None:
            abort(400)
        trip = get_and_pack_trip(trip_id)
        members = [trip["members"][i]["userId"] for i in range(len(trip["members"]))]
        if token_id not in members:
            abort(403)
    elif request.method == "POST":
        trip_data = json.loads(request.data)
        if trip_data["members"] is None:
            abort(401)
        if int(token_id) not in trip_data["members"]:
            abort(403)
        trip_id = trip_entity.create_trip(
            name=trip_data["name"],
            start_date=trip_data["startDate"],
            end_date=trip_data["endDate"],
            experiences=trip_data["experiences"],
            members=trip_data["members"],
        )
        return get_and_pack_trip(trip_id)
    elif request.method == "PATCH":
        if trip_id is None:
            abort(400)
        trip_data = json.loads(request.data)
        if trip_data["members"] is None:
            abort(401)
        if int(token_id) not in trip_data["members"]:
            abort(403)
        if (
            trip_entity.update_trip(
                trip_id=trip_id,
                name=trip_data["name"],
                start_date=trip_data["startDate"],
                end_date=trip_data["endDate"],
                experiences=trip_data["experiences"],
                members=trip_data["members"],
            )
            == 1
        ):
            abort(404)
        return get_and_pack_trip(trip_id)
    elif request.method == "DELETE":
        if trip_id is None:
            abort(400)
        response = trip_entity.delete_trip(trip_id, token_id)
        if response == 1:
            abort(404)
        elif response == 2:
            abort(403)
        return "Successfully Deleted"


@trip_bp.route("/user/<user_id>", methods=["GET"])
@validate_token
def get_trips_by_user(token_id, user_id=None):
    if user_id is not None:
        if user_id != token_id:
            abort(403)
        trip_array = []
        ids = trip_entity.get_trip_ids_by_user(user_id)
        for id in ids:
            trip_array.append(get_and_pack_trip(id[0]))
        return json.dumps({"trips": trip_array})
    else:
        abort(400)
