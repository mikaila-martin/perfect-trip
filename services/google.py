import requests
from config import google_places_api_key


def places_autocomplete(query):
    url = f"https://maps.googleapis.com/maps/api/place/autocomplete/json?key={google_places_api_key}&input={query}"
    result = requests.get(url)
    return result.json()
