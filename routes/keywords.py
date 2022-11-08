from flask import Blueprint, Response
import database.keyword as keyword_service
import json

keywords_bp = Blueprint("keywords", __name__)


@keywords_bp.route("/keywords", methods=["GET"])
def get_keywords():

    keywords = keyword_service.get_keywords()
    return Response(json.dumps({"keywords": keywords}), status=200)
