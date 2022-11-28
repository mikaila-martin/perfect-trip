from flask import Blueprint, request, Response
from middleware.auth import validate_token
import database.trip as trip_entity
import json

trip_bp = Blueprint("trip", __name__)


@trip_bp.route("/", methods=["GET"])
@validate_token
def get_user_trips(user_id):
    try:

        trip_ids = trip_entity.get_trip_ids_by_user(user_id)

        trips = []

        for id in trip_ids:
            trips.append(trip_entity.get_trip(id["trip_id"]))

        return json.dumps({"trips": trips})

    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@trip_bp.route("/<trip_id>", methods=["GET"])
@validate_token
def get_itinerary(user_id, trip_id):
    try:

        trip = trip_entity.get_trip(trip_id)

        member_ids = [trip["members"][i]["userId"] for i in range(len(trip["members"]))]

        if user_id not in member_ids:
            return Response(
                json.dumps({"message": "Trip does not belong to user."}), status=400
            )

        return Response(json.dumps({"trip": trip}), status=200)

    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@trip_bp.route("/", methods=["POST"])
@validate_token
def post_itinerary(user_id):
    try:

        data = json.loads(request.data)

        if len(data["members"]) == 0:
            return Response(
                json.dumps({"message": "Trip must have members."}), status=400
            )

        trip = trip_entity.create_trip(
            name=data["name"],
            start_date=data["startDate"],
            end_date=data["endDate"],
            itinerary=data["itinerary"],
            members=data["members"],
        )

        return Response(json.dumps({"trip": trip}), status=200)

    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@trip_bp.route("/<trip_id>", methods=["PATCH"])
@validate_token
def update_itinerary(user_id, trip_id):
    try:

        data = json.loads(request.data)

        if len(data["members"]) == 0:
            return Response(
                json.dumps({"message": "Trip must have members."}), status=400
            )

        trip = trip_entity.get_trip(trip_id)

        member_ids = [trip["members"][i]["userId"] for i in range(len(trip["members"]))]

        if user_id not in member_ids:
            return Response(
                json.dumps({"message": "Trip does not belong to user."}), status=400
            )

        trip = trip_entity.update_trip(
            trip_id=trip_id,
            name=data["name"],
            start_date=data["startDate"],
            end_date=data["endDate"],
            itinerary=data["itinerary"],
            members=data["members"],
        )

        return Response(json.dumps({"trip": trip}), status=200)

    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@trip_bp.route("/<trip_id>", methods=["DELETE"])
@validate_token
def delete_itinerary(user_id, trip_id):
    try:

        trip = trip_entity.get_trip(trip_id)

        member_ids = [trip["members"][i]["userId"] for i in range(len(trip["members"]))]

        if user_id not in member_ids:
            return Response(
                json.dumps({"message": "Trip does not belong to user."}), status=400
            )

        trip_entity.delete_trip(trip_id)

        return Response(json.dumps({"tripId": trip_id}), status=200)

    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)
