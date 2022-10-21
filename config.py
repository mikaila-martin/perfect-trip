import os
from dotenv import load_dotenv

load_dotenv()

env = os.getenv("PYTHON_ENV") or "development"

postgres = {
    "production": {
        "host": os.getenv("POSTGRES_PROD_HOST"),
        "database": os.getenv("POSTGRES_PROD_DATABASE"),
        "user": os.getenv("POSTGRES_PROD_USER"),
        "password": os.getenv("POSTGRES_PROD_PASSWORD"),
        "port": os.getenv("POSTGRES_PROD_PORT"),
    },
    "development": {
        "host": os.getenv("POSTGRES_DEV_HOST"),
        "database": os.getenv("POSTGRES_DEV_DATABASE"),
        "user": os.getenv("POSTGRES_DEV_USER"),
        "password": os.getenv("POSTGRES_DEV_PASSWORD"),
        "port": os.getenv("POSTGRES_DEV_PORT"),
    },
}

google_places_api_key = os.getenv("GOOGLE_PLACES_API_KEY")
