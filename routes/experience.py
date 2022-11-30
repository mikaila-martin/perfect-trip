from flask import Blueprint, request, Response
import database.experience as experience_service
from middleware.auth import validate_token
from services.google import places_nearby, places_details
from services.aws import upload_image, delete_image
from util import get_country, is_valid_uuid
import json

experience_bp = Blueprint("experience", __name__)


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

    return json.dumps({"experiences": experiences + places})


@experience_bp.route("/", methods=["GET"])
@validate_token
def get_user_experiences(user_id):

    # Get experiences
    try:

        experiences = experience_service.get_experiences_by_user_id(user_id)
        return Response(json.dumps({"experiences": experiences}), status=200)

    # Handle exception
    except TypeError:
        return Response(json.dumps({"experiences": []}), status=200)

    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@experience_bp.route("/<exp_id>", methods=["GET"])
def get_experience(exp_id):

    # Get experience
    try:

        # Get experience from database
        if is_valid_uuid(exp_id):
            experience = experience_service.get_experience_by_id(exp_id)
            return Response(json.dumps({"experience": experience}), status=200)

        # Get experience from google
        else:
            experience = places_details(exp_id)
            return Response(json.dumps({"experience": experience}), status=200)

    # Handle exception
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@experience_bp.route("/", methods=["POST"])
@validate_token
def create_experience(user_id):

    try:

        # Get data from request
        data = json.loads(request.data)

        # Get country from coordinates
        country = get_country(data["latitude"], data["longitude"])

        # Upload images to AWS S3 and build url list
        images = []
        for image in data["images"]:
            image_key = upload_image(image)
            images.append(image_key)

        images = ",".join(images)

        # Create experience
        experience = experience_service.create_experience(
            {
                "user_id": user_id,
                "title": data["title"],
                "description": data["description"],
                "keywords": data["keywords"],
                "latitude": data["latitude"],
                "longitude": data["longitude"],
                "images": images,
                "country_name": country["name"],
                "country_code": country["code"],
            }
        )
        return Response(json.dumps({"experience": experience}), status=200)

    # Handle exception
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@experience_bp.route("/<exp_id>", methods=["PATCH"])
@validate_token
def update_experience(user_id, exp_id):

    try:

        # Get data from request
        data = json.loads(request.data)

        # Get country from coordinates
        country = get_country(data["latitude"], data["longitude"])

        # Build updated image url list
        updated_images = []
        previous_images = experience_service.get_images(exp_id).split(",")

        for image in data["images"]:

            # Keep previous images
            if image in previous_images:

                updated_images.append(image)
                previous_images.remove(image)

            # Upload new images
            else:

                image_key = upload_image(image)
                updated_images.append(image_key)

        # Remove deleted images
        for image in previous_images:

            image_key = image.split("/")[-1]
            delete_image(image_key)

        # Convert image list to comma delimited string
        images = ",".join(updated_images)

        # Update experience
        experience = experience_service.update_experience(
            {
                "exp_id": exp_id,
                "user_id": user_id,
                "title": data["title"],
                "description": data["description"],
                "keywords": data["keywords"],
                "latitude": data["latitude"],
                "longitude": data["longitude"],
                "images": images,
                "country": country,
            },
        )
        return Response(json.dumps({"experience": experience}), status=200)

    # Handle exception
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@experience_bp.route("/<exp_id>", methods=["DELETE"])
@validate_token
def delete_experience(user_id, exp_id):

    try:

        # Delete images
        images = experience_service.get_images(exp_id).split(",")

        for image in images:

            image_key = image.split("/")[-1]
            delete_image(image_key)

        # Delete experience
        experience_service.delete_experience(user_id, exp_id)
        return Response(json.dumps({"exp_id": exp_id}), status=200)

    # Handle exception
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)
