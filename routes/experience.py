from flask import Blueprint, request, Response
import database.experience as experience_service
from middleware.auth import validate_token
from services.google import places_nearby
from util import get_country
import json

experience_bp = Blueprint("experience", __name__)

# PLACEHOLDER IMAGES
images = "https://via.placeholder.com/150/0000FF/FFFFFF?Text=PHOTO_1,https://via.placeholder.com/150/0000FF/FFFFFF?Text=PHOTO_2,https://via.placeholder.com/150/0000FF/FFFFFF?Text=PHOTO_3"


@experience_bp.route("/search", methods=["GET"])
def search():

    # Extract keywords
    keywords = request.args.get("keywords")
    keywords = [] if keywords == "" else keywords.split(",")

    # Extract map center
    c_lat = float(request.args.get("c_lat"))
    c_lng = float(request.args.get("c_lng"))

    # Get experiences from Google
    places = places_nearby(c_lat, c_lng, keywords)

    # Extract map bounding box
    ne_lat = float(request.args.get("ne_lat"))
    ne_lng = float(request.args.get("ne_lng"))
    sw_lat = float(request.args.get("sw_lat"))
    sw_lng = float(request.args.get("sw_lng"))

    # Get experiences from database
    experiences = experience_service.search_experiences(
        ne_lat, sw_lat, ne_lng, sw_lng, keywords
    )

    return json.dumps({"experiences": experiences, "places": places})


@experience_bp.route("/<exp_id>", methods=["GET"])
def get_experience(exp_id):

    # Get experience
    try:

        experience = experience_service.get_experience_by_id(exp_id)
        return Response(json.dumps({"experience": experience}), status=200)

    # Handle exception
    except Exception as message:

        return Response(json.dumps({"message": str(message)}), status=400)


@experience_bp.route("/user/<user_id>", methods=["GET"])
def get_user_experiences(user_id):

    # Get experiences
    try:

        experiences = experience_service.get_experiences_by_user_id(user_id)
        return Response(json.dumps({"experiences": experiences}), status=200)

    # Handle exception
    except Exception as message:

        return Response(json.dumps({"message": str(message)}), status=400)


@experience_bp.route("/", methods=["POST"])
@validate_token
def create_experience(user_id):
    data = json.loads(request.data)

    # Get country from coordinates
    country = get_country(data["latitude"], data["longitude"])

    # TODO: Upload images to AWS S3 and get URLs

    # Create experience
    try:
        experience = experience_service.create_experience(
            {
                "user_id": user_id,
                "title": data["title"],
                "description": data["description"],
                "keywords": data["keywords"],
                "latitude": data["latitude"],
                "longitude": data["longitude"],
                "exp_start": data["exp_start"],
                "exp_end": data["exp_end"],
                "images": images,
                "country": country,
            }
        )
        return Response(json.dumps({"experience": experience}), status=200)

    # Handle exception
    except Exception as message:

        return Response(json.dumps({"message": str(message)}), status=400)


@experience_bp.route("/<exp_id>", methods=["PATCH"])
@validate_token
def update_experience(user_id, exp_id):
    data = json.loads(request.data)

    # Get country from coordinates
    country = get_country(data["latitude"], data["longitude"])

    # TODO: Upload images to AWS S3 and get URLs

    # Update experience
    try:

        experience = experience_service.update_experience(
            {
                "user_id": user_id,
                "exp_id": exp_id,
                "title": data["title"],
                "description": data["description"],
                "keywords": data["keywords"],
                "latitude": data["latitude"],
                "longitude": data["longitude"],
                "exp_start": data["exp_start"],
                "exp_end": data["exp_end"],
                "images": images,
                "country": country,
            }
        )
        return Response(json.dumps({"experience": experience}), status=200)

    # Handle exception
    except Exception as message:

        return Response(json.dumps({"message": str(message)}), status=400)


@experience_bp.route("/<exp_id>", methods=["DELETE"])
@validate_token
def delete_experience(user_id, exp_id):

    # Delete experience
    try:

        experience_service.delete_experience(user_id, exp_id)
        return Response(json.dumps({"exp_id": exp_id}), status=200)

    # Handle exception
    except Exception as message:

        return Response(json.dumps({"message": str(message)}), status=400)
