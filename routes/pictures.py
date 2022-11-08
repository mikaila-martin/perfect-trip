from flask import Blueprint, request, Response
from services.aws import *
import json
import base64

picture_bp = Blueprint("pictures", __name__)


@picture_bp.route("/<file_name>", methods=["GET"])
def get_image(file_name):
    try:
        picture = get_picture(file_name)
        pic_64 = base64.b64encode(picture).decode("utf-8")
        return Response(json.dumps({"picture":pic_64}), status=200)
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@picture_bp.route("/<file_name>", methods=["POST"])
def post_image(file_name):
    try:
        data = json.loads(request.data)
        picture = data["picture"]
        picture_raw = base64.b64decode(picture.encode("utf-8"))
        upload_picture(file_name, picture_raw)
        return Response(json.dumps({"file name": file_name}), status=200)
    except Exception as message:
        return Response(json.dumps({"message": str(message)}), status=400)


@picture_bp.route("/<file_name>", methods=["DELETE"])
def delete_image(file_name):
    delete_picture(file_name)
    return Response(json.dumps({"file name": file_name}), status=200)
