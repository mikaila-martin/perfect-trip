from flask import Blueprint, request, Response
from middleware.auth import validate_token
import database.experience as experience_entity
import database.trip as trip_entity
import json

trip_bp = Blueprint("trip", __name__)


def get_and_pack_trip(trip_id):
    itin_data, exp_data, user_data = trip_entity.get_trip(trip_id)
    experiences_table = []
    for experience in exp_data:
        packed_experience = experience_entity.get_experience_by_id(experience["exp_id"])
        experiences_table.append(
            {
                "experience": packed_experience,
                "date": str(experience["itin_date"]),
                "time": str(experience["time"]),
            }
        )
    user_table = []
    for user in user_data:
        user_table.append({"userId": user["user_id"],
                           "username": user["email"],
                           "avatar": user["username"]})
    packed_trip = {
        "tripID": itin_data[0]["trip_id"],
        "name": itin_data[0]["trip_name"],
        "startDate": str(itin_data[0]["trip_start"]),
        "endDate": str(itin_data[0]["trip_end"]),
        "experiences": experiences_table,
        "members": user_table,
    }
    return packed_trip


@trip_bp.route("/<trip_id>", methods=["GET"])
@validate_token
def get_itinerary(user_id, trip_id):
    try:
        trip = get_and_pack_trip(trip_id)
        members = [trip["members"][i]["userId"] for i in range(len(trip["members"]))]
        if user_id not in members:
            return Response(json.dumps({"message": "Trip does not belong to user."}), status=400)
        return Response(json.dumps({"trip": trip}), status=200)
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@trip_bp.route("/", methods=["POST"])
@validate_token
def post_itinerary(user_id):
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
def update_itinerary(user_id, trip_id):
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
def delete_itinerary(user_id, trip_id):
    try:
        trip_entity.delete_trip(user_id, trip_id)
        return "Trip Deleted"
    #except Exception as message:
    #    return Response(json.dumps({"message": str(message)}), status=400)
    finally:
        pass


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

