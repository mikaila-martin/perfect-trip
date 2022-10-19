from flask import Flask
from database import connect_to_database
from dotenv import load_dotenv

# from flask_login import LoginManager

load_dotenv()

app = Flask(__name__)

# app.secret_key = 0xd4de4a47758fde65583a7a0cc693ec0

# login_manager = LoginManager()
# login_manager.init_app(app)


def main():
    app.run(host="localhost", port=8080)
    connect_to_database()  # is this necessary?


if __name__ == "__main__":
    main()
