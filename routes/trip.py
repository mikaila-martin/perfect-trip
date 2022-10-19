from flask import abort, request
from database import *
from app import app
import json


@app.route("/trip/<trip_id>", methods=["GET", "POST", "PATCH", "DELETE"])
def trip(trip_id=None):
    if trip_id is None:
        return abort(400)
    if request.method == "GET":
        return get_trip(trip_id)
    elif request.method == "POST":
        trip_data = json.loads(request.data)
        return make_trip(
            name=trip_data["name"],
            start_date=trip_data["startDate"],
            end_date=trip_data["endDate"],
            experiences=trip_data["experiences"],
            members=trip_data["members"],
        )
    elif request.method == "PATCH":
        trip_data = json.loads(request.data)
        return update_trip(
            trip_id=trip_id,
            name=trip_data["name"],
            start_date=trip_data["startDate"],
            end_date=trip_data["endDate"],
            experiences=trip_data["experiences"],
            members=trip_data["members"],
        )
    elif request.method == "DELETE":
        return delete_trip(trip_id)


@app.route("/trips/<user_id>", methods=["GET"])
def get_trips_by_user(user_id=None):
    if user_id is not None:
        return get_trips_by_user(user_id)
    else:
        return abort(400)
