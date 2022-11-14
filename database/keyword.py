from database.connection import get_query
from util import pack_keywords


def get_keywords():
    keywords = get_query(f"SELECT * from pt_schema.keywords")
    return pack_keywords(keywords)
