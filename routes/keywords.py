from flask import Blueprint
import database.keyword as keyword_service
import json

keywords_bp = Blueprint("keywords", __name__)


@keywords_bp.route("/keywords", methods=["GET"])
def get_keywords():

    response = keyword_service.get_keywords()
    keywords = pack_keywords(response)

    return json.dumps({"keywords": keywords})
