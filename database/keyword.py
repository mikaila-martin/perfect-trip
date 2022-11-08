from database.config import query
from util import pack_keywords


def get_keywords():
    keywords = query(f"SELECT * from pt_schema.keywords")
    return pack_keywords(keywords)
