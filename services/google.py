import requests
from config import google_places_api_key, keyword_list

BASE_URL = "https://maps.googleapis.com/maps/api/place"


def places_details(place_id):
    """"""
    url = f"{BASE_URL}/details/json?key={google_places_api_key}&place_id={place_id}"

    response = requests.get(url)
    json_response = response.json()

    status = json_response["status"]
    result = json_response["result"]

    if status == "OK":

        # Get photo urls
        images = []

        if "photos" in result:
            for photo in result["photos"]:
                url = f'{BASE_URL}/photo?key={google_places_api_key}&photo_reference={photo["photo_reference"]}&maxwidth=400'
                images.append(url)

        # Return none if there are no photos
        if len(images) == 0:
            return None

        # Get location details
        city = None
        country_name = None
        country_code = None

        for component in result["address_components"]:
            for type in component["types"]:
                if type == "locality":
                    city = component["long_name"]
                if type == "country":
                    country_name = component["long_name"]
                    country_code = component["short_name"]

        # Get reviews
        reviews = []

        if "reviews" in result:
            for review in result["reviews"]:
                reviews.append(
                    {
                        "rating": review["rating"],
                        "comment": review["text"],
                        "user": {
                            "username": review["author_name"],
                            "avatar": review["profile_photo_url"],
                        },
                    }
                )

        # Get description
        description = None

        if "editorial_summary" in result:
            description = result["editorial_summary"]["overview"]

        # Get rating
        rating = None

        if "rating" in result:
            rating = result["rating"]

        # Get keywords
        types = []

        for type in result["types"]:
            if type in keyword_list:
                types.append(type)

        # Format place object
        place = {
            "id": place_id,
            "title": result["name"],
            "description": description,
            "keywords": types,
            "reviews": reviews,
            "rating": rating,
            "images": images,
            "city": city,
            "countryName": country_name,
            "countryCode": country_code.lower(),
            "latitude": round(result["geometry"]["location"]["lat"], 4),
            "longitude": round(result["geometry"]["location"]["lng"], 4),
        }

        return place

    else:
        return None


def places_autocomplete(query):
    """"""
    url = f"{BASE_URL}/autocomplete/json?key={google_places_api_key}&input={query}"

    response = requests.get(url)
    json_response = response.json()

    status = json_response["status"]
    predictions = json_response["predictions"]

    places = []

    if status == "OK":
        for prediction in predictions:

            place_id = prediction["place_id"]
            place = places_details(place_id)

            if place is not None:
                places.append(place)

    return places


def places_nearby(lat, lng, keywords):
    """"""

    urls = []

    if len(keywords) == 0:
        urls.append(
            f"{BASE_URL}/nearbysearch/json?key={google_places_api_key}&location={lat},{lng}&radius=50000&language=en"
        )

    else:
        for keyword in keywords:
            urls.append(
                f"{BASE_URL}/nearbysearch/json?key={google_places_api_key}&location={lat},{lng}&radius=50000&language=en&type={keyword}"
            )

    places = []

    for url in urls:

        response = requests.get(url)
        json_response = response.json()

        status = json_response["status"]
        results = json_response["results"]

        if status == "OK":
            for result in results:

                is_valid_place = False

                for type in result["types"]:
                    if type in keyword_list:
                        is_valid_place = True

                if is_valid_place:
                    place_id = result["place_id"]
                    place = places_details(place_id)

                    if place is not None:
                        places.append(place)

    return places
