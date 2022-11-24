from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="geoapiExercises")


def get_country(latitude, longitude):
    location = geolocator.reverse(f"{latitude},{longitude}")
    address = location.raw["address"]
    country = address.get("country", "")
    return country


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
        "country": exp_data["country"],
        "creator": {
            "userId": user_data["user_id"],
            "username": user_data["username"],
            "avatar": user_data["avatar"],
        },
        "reviews": review_list,
    }
    return packed_experience
