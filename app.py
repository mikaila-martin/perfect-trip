from flask import Flask, request
from flask_cors import CORS
from database import connect_to_database
from dotenv import load_dotenv

load_dotenv()

# Import blueprints (routes)
from routes.auth import auth_bp
from routes.user import user_bp
from routes.trip import trip_bp
from routes.places import places_bp
from routes.experience import experience_bp

# Initialize app
app = Flask(__name__)

CORS(app)  # Handle cors errors

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(trip_bp, url_prefix="/trip")
app.register_blueprint(places_bp, url_prefix="/places")
app.register_blueprint(experience_bp, url_prefix="/experience")


def main():
    app.run(host="localhost", port=8080)
    connect_to_database()  # is this necessary?


if __name__ == "__main__":
    main()
