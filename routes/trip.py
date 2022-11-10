from flask import Blueprint, request, Response
from middleware.auth import validate_token
import database.experience as experience_entity
import database.trip as trip_entity
import json
from util import pack_experience

trip_bp = Blueprint("trip", __name__)


def get_and_pack_trip(trip_id):
    itin_data, exp_data, user_data = trip_entity.get_trip(trip_id)
    experiences_table = []
    for experience in exp_data:
        exp_info = experience_entity.get_experience_by_id(experience[0])
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


@trip_bp.route("/<trip_id>", methods=["GET"])
@validate_token
def get_trip(user_id, trip_id):
    try:
        trip = get_and_pack_trip(trip_id)
        members = [trip["members"][i]["userId"] for i in range(len(trip["members"]))]
        if user_id not in members:
            return Response(json.dumps({"message": "Trip does not belong to user."}), status=400)
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@trip_bp.route("/", methods=["POST"])
@validate_token
def post_trip(user_id):
    try:
        trip_data = json.loads(request.data)
        if trip_data["members"] is None:
            return Response(json.dumps({"message": "Trip must have members."}), status=400)
        if int(user_id) not in trip_data["members"]:
            return Response(json.dumps({"message": "Trip does not belong to user."}), status=400)
        trip_id = trip_entity.create_trip(
            name=trip_data["name"],
            start_date=trip_data["startDate"],
            end_date=trip_data["endDate"],
            experiences=trip_data["experiences"],
            members=trip_data["members"],
        )
        return get_and_pack_trip(trip_id)
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@trip_bp.route("/<trip_id>", methods=["PATCH"])
@validate_token
def update_trip(user_id, trip_id):
    try:
        trip_data = json.loads(request.data)
        if trip_data["members"] is None:
            return Response(json.dumps({"message": "Trip must have members."}), status=400)
        if int(user_id) not in trip_data["members"]:
            return Response(json.dumps({"message": "Trip does not belong to user."}), status=400)
        trip_entity.update_trip(
                trip_id=trip_id,
                name=trip_data["name"],
                start_date=trip_data["startDate"],
                end_date=trip_data["endDate"],
                experiences=trip_data["experiences"],
                members=trip_data["members"])

        return get_and_pack_trip(trip_id)
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@trip_bp.route("/<trip_id>", methods=["DELETE"])
@validate_token
def update_trip(user_id, trip_id):
    try:
        trip_entity.delete_trip(trip_id, user_id)
        return "Trip Deleted"
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@trip_bp.route("/user/", methods=["GET"])
@validate_token
def get_trips_by_user(user_id):
    try:
        trip_array = []
        ids = trip_entity.get_trip_ids_by_user(user_id)
        for id in ids:
            trip_array.append(get_and_pack_trip(id[0]))
        return json.dumps({"trips": trip_array})
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)

