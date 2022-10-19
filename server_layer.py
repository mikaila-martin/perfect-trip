import json
import hashlib
#from flask_login import LoginManager
from flask import Flask, session, request, abort
from database_layer import *


app = Flask(__name__)

#app.secret_key = 0xd4de4a47758fde65583a7a0cc693ec0

#login_manager = LoginManager()
#login_manager.init_app(app)


def hash_password(password):
    password = password.encode()
    password_hash = hashlib.sha224(password)
    return password_hash.digest().hex()


@app.route('/auth/login', methods=["POST"])
def login():
    login_info = json.loads(request.data)
    username = login_info["username"]
    password = login_info["password"]
    password_hash = hash_password(password)
    login_response = login_user(username, password_hash)
    if login_response == 1:
        abort(403)
    else:
        return json.dumps({"userId":login_response[0],
                           "username":login_response[1],
                           "avatar":login_response[2]})


@app.route('/auth/register', methods=["POST"])
def register():
    registration_info = json.loads(request.data)
    username = registration_info["username"]
    password_a = registration_info["passwordA"]
    password_b = registration_info["passwordB"]
    email = registration_info["email"]
    if password_b != password_a:
        return "PASSWORD NOT EQUAL FLOPPA ERROR"
    else:
        password_hash = hash_password(password_b)
        registration_response = register_user(username, password_hash, email)
        if registration_response == 1:
            return "EMAIL IN USE FLOPPA ERROR"
        return json.dumps({"userId":registration_response[0],
                           "username":registration_response[1],
                           "avatar":registration_response[2]})


@app.route('/search', methods=["POST"])
def search():
    search_parameters = json.loads(request.data)
    return search_db(search_parameters["location_coords"],
                     search_parameters["keywords"])


def pack_reviews(review_data):
    review_list = []
    for tup in review_data:
        review = {"reviewId": tup[0],
                  "rating": tup[1],
                  "comment": tup[2],
                  "user": {"userId": tup[3],
                           "username": tup[4],
                           "avatar": tup[5]
                           }
                  }
        review_list.append(review)
    return review_list


def pack_experience(experience_data, user_data, review_data):
    review_list = pack_reviews(review_data)
    packed_experience = {"experienceId": experience_data[0],
                         "name": experience_data[2],
                         "description": experience_data[3],
                         "keywords": "array[string]",
                         "coordinates": {"lat": experience_data[4],
                                         "lon": experience_data[5]
                                         },
                         "dates": {"start": str(experience_data[6]),
                                   "end": str(experience_data[7])
                                   },
                         "images": experience_data[8],
                         "country": experience_data[9],
                         "creator": {"userId": user_data[0],
                                     "username": user_data[1],
                                     "avatar": user_data[2]
                                     },
                         "reviews": review_list
                         }
    return packed_experience


@app.route('/experience', methods=["GET", "POST", "PATCH", "DELETE"])
@app.route('/experience/<exp_id>', methods=["GET", "POST", "PATCH", "DELETE"])
@app.route('/experience/<exp_id>/<rev_id>', methods=["GET", "POST", "PATCH", "DELETE"])
def experience(exp_id=None, rev_id=None):
    if request.method == "GET":
        if exp_id is not None and rev_id is not None:
            response = get_review(rev_id)
            if response == 1:
                abort(404)
            else:
                return json.dumps(pack_reviews(response)[0])
        elif exp_id is not None and rev_id is None:
            response = get_experience(exp_id)
            if response == 1:
                abort(404)
            else:
                experience_data, user_data, review_data = response[0], response[1], response[2]
                return json.dumps(pack_experience(experience_data, user_data, review_data))
        else:
            abort(400)
    elif request.method == "POST":
        if exp_id is not None:
            review_data = json.loads(request.data)
            response = make_review(review_data["userId"], exp_id,
                                   review_data["rating"],
                                   review_data["comment"])
            if response == 1:
                abort(403)
            return json.dumps(pack_reviews(response))
        else:
            experience_data = json.loads(request.data)
            response = make_experience(user_id=experience_data["userId"],
                                       name=experience_data["name"],
                                       pictures=experience_data["images"],
                                       description=experience_data["description"],
                                       coords=experience_data["coordinates"],
                                       keywords=experience_data["keywords"],
                                       country=experience_data["country"],
                                       start=experience_data["dates"]["start"],
                                       end=experience_data["dates"]["end"])
            if response == 2:
                abort(403)
            return json.dumps(pack_experience(response[0], response[1], response[2]))
    elif request.method == "PATCH":
        if exp_id is not None and rev_id is not None:
            review_data = json.loads(request.data)
            response = update_review(review_data['userId'], rev_id,
                                     review_data['rating'],
                                     review_data['comment'])
            if response == 1:
                abort(404)
            if response == 2:
                abort(403)
            return json.dumps(pack_reviews(response))
        elif exp_id is not None:
            experience_data = json.loads(request.data)
            response = update_experience(exp_id=exp_id,
                                     user_id=experience_data["userId"],
                                     name=experience_data["name"],
                                     pictures=experience_data["images"],
                                     description=experience_data["description"],
                                     coords=experience_data["coordinates"],
                                     keywords=experience_data["keywords"],
                                     country=experience_data["country"],
                                     start=experience_data["dates"]["start"],
                                     end=experience_data["dates"]["end"])
            if response == 1:
                abort(404)
            if response == 2:
                abort(403)
            return json.dumps(pack_experience(response[0], response[1], response[2]))
        else:
            abort(400)
    elif request.method == "DELETE":
        if exp_id is not None and rev_id is not None:
            response = delete_review(rev_id)
            if response == 1:
                abort(404)
            return
        elif exp_id is not None:
            response = delete_experience(exp_id)
            if response == 1:
                abort(404)
            return
        else:
            abort(400)


@app.route('/trip/<trip_id>', methods=["GET", "POST", "PATCH", "DELETE"])
def trip(trip_id=None):
    if trip_id is None:
        return abort(400)
    if request.method == "GET":
        return get_trip(trip_id)
    elif request.method == "POST":
        trip_data = json.loads(request.data)
        return make_trip(name=trip_data["name"],
                         start_date=trip_data["startDate"],
                         end_date=trip_data["endDate"],
                         experiences=trip_data["experiences"],
                         members=trip_data["members"]
                         )
    elif request.method == "PATCH":
        trip_data = json.loads(request.data)
        return update_trip(trip_id=trip_id,
                           name=trip_data["name"],
                           start_date=trip_data["startDate"],
                           end_date=trip_data["endDate"],
                           experiences=trip_data["experiences"],
                           members=trip_data["members"]
                           )
    elif request.method == "DELETE":
        return delete_trip(trip_id)


@app.route('/trips/<user_id>', methods=["GET"])
def get_trips_by_user(user_id=None):
    if user_id is not None:
        return get_trips_by_user(user_id)
    else:
        return abort(400)


@app.route('/experiences/<user_id>', methods=["GET"])
def get_experiences_by_user(user_id):
    if user_id is not None:
        return get_experiences_by_user(user_id)
    else:
        return abort(400)


def main():
    app.run(host="localhost", port=8080)
    connect_to_database()


if __name__ == "__main__":
    main()






