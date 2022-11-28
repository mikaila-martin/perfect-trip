from datetime import datetime
from geopy.geocoders import Nominatim
import country_converter as coco
import uuid


def get_date_string(date):
    if date is None:
        return None
    else:
        return date.strftime("%Y-%m-%d")


def get_time_string(time):
    if time is None:
        return None
    else:
        return time.strftime("%I:%M %p")


def is_valid_uuid(val):
    try:
        uuid.UUID(val)
        return True
    except ValueError:
        return False


geolocator = Nominatim(user_agent="geoapiExercises")


def get_country(latitude, longitude):
    location = geolocator.reverse(f"{latitude},{longitude}")
    address = location.raw["address"]
    name = address.get("country", "")
    code = coco.convert(names=[name], to="ISO2").lower()
    return {"name": name, "code": code}


def pack_reviews(data):
    reviews = []

    if data is None:
        return reviews

    for row in data:
        review = {
            "reviewId": row["review_id"],
            "rating": row["rev_rating"],
            "comment": row["comment"],
            "user": {
                "userId": row["user_id"],
                "username": row["username"],
                "avatar": row["username"],
            },
        }
        reviews.append(review)

    return reviews


def pack_keywords(data):
    keywords = []

    for row in data:
        keywords.append(row["keyword"])

    return keywords


def pack_experience(exp_data, user_data, review_data, keyword_data):
    review_list = pack_reviews(review_data)
    keywords_list = pack_keywords(keyword_data)
    packed_experience = {
        "id": exp_data["exp_id"],
        "title": exp_data["title"],
        "description": exp_data["description"],
        "keywords": keywords_list,
        "latitude": float(exp_data["latitude"]),
        "longitude": float(exp_data["longitude"]),
        "images": exp_data["images"].split(","),
        "countryName": exp_data["country_name"],
        "countryCode": exp_data["country_code"],
        "creator": {
            "userId": user_data["user_id"],
            "username": user_data["username"],
            "avatar": user_data["avatar"],
        },
        "reviews": review_list,
    }
    return packed_experience
