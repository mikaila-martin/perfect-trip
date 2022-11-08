from flask import Flask
from flask_cors import CORS

# Import config
from config import env

# Import blueprints (routes)
from routes.auth import auth_bp
from routes.user import user_bp
from routes.trip import trip_bp
from routes.places import places_bp
from routes.experience import experience_bp
from routes.pictures import picture_bp

# Initialize app
app = Flask(__name__)

# Middleware
CORS(app)

# Register blueprints (routes)
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(trip_bp, url_prefix="/trip")
app.register_blueprint(places_bp, url_prefix="/places")
app.register_blueprint(experience_bp, url_prefix="/experience")
app.register_blueprint(picture_bp, url_prefix="/picture")

# Start server
if __name__ == "__main__":
    app.run(debug=env == "development")
