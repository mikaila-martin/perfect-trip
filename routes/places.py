from flask import abort, request
from app import app

from services.google import places_autocomplete


@app.route("/places", methods=["GET"])
def get_places():
    query = request.args.get("query")
    places = places_autocomplete(query)
    return places
