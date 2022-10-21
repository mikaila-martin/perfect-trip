import requests
from config import google_places_api_key

BASE_URL = "https://maps.googleapis.com/maps/api/place"


def places_details(place_id):
    """"""
    url = f"{BASE_URL}/details/json?key={google_places_api_key}&place_id={place_id}"

    response = requests.get(url)
    json_response = response.json()

    status = json_response["status"]
    result = json_response["result"]

    if status == "OK":

        city = None
        country = None
        country_code = None

        for component in result["address_components"]:
            for type in component["types"]:
                if type == "locality":
                    city = component["long_name"]
                if type == "country":
                    country = component["long_name"]
                    country_code = component["short_name"]

        place = {
            "id": result["place_id"],
            "name": result["name"],
            "city": city,
            "country": country,
            "country_code": country_code.lower(),
            "coords": {
                "lat": round(result["geometry"]["location"]["lat"], 4),
                "lng": round(result["geometry"]["location"]["lng"], 4),
            },
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

    else:
        return None


def places_nearby(lat, lng):
    """"""
    url = (
        f"{BASE_URL}/nearbysearch/json?key={google_places_api_key}&location={lat},{lng}"
    )

    response = requests.get(url)
    json_response = response.json()

    print(json_response)
