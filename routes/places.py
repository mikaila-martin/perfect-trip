from flask import Blueprint, request
from services.google import places_autocomplete

places_bp = Blueprint("places", __name__)


@places_bp.route("/", methods=["GET"])
def get_places():
    query = request.args.get("query")
    places = places_autocomplete(query)
    return {"places": places}
