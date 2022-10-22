import psycopg2 as db
from config import env, postgres
import os

# Information on psycopg2 library from
# https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries
# 10/12/2022


def connect_to_database():
    """Connects to the database associated with the information given in the
    config.py file."""
    connection = db.connect(
        host=postgres[env]["host"],
        database=postgres[env]["database"],
        user=postgres[env]["user"],
        password=postgres[env]["password"],
        port=postgres[env]["port"]
    )

    cur = connection.cursor()
    return connection, cur


def get_query(query):
    """Takes in a query string and returns the result of running that SQL
    query for the database."""
    connection, cursor = connect_to_database()
    cursor.execute(query)
    data = cursor.fetchall()
    connection.close()
    cursor.close()
    return data


def send_query(query):
    """Takes in a query string. Modifies the database by running the SQL query.
    Does not return anything."""
    connection, cursor = connect_to_database()
    cursor.execute(query)
    connection.commit()
    connection.close()
    cursor.close()


def register_user(username, password_hash, email):
    if get_query(f"SELECT * FROM pt_schema.users WHERE email = '{email}';"):
        return 1
    else:
        send_query(
            "INSERT INTO pt_schema.users (username, password, email) "
            f"VALUES ('{username}', '{password_hash}', '{email}');"
        )
        user_id = get_query(
            f"SELECT users.user_id FROM pt_schema.users WHERE email = '{email}';"
        )[0][0]
        return user_id, email, username


def login_user(email, password):
    if not get_query(
        f"SELECT * FROM pt_schema.users "
        f"WHERE users.email = '{email}' AND users.password = '{password}'"
    ):
        return 1
    else:
        user_id, username = get_query(
            f"SELECT user_id, username FROM pt_schema.users WHERE email = '{email}'"
        )[0]
        return user_id, email, username


def get_experience(exp_id):
    experience_data = get_query(
        f"SELECT experiences.exp_id, experiences.user_id, experiences.title, "
        f"experiences.description, experiences.latitude, experiences.longitude, "
        f"experiences.exp_start, experiences.exp_end, experiences.image, "
        f"experiences.country FROM pt_schema.experiences "
        f"WHERE experiences.exp_id = '{exp_id}'"
    )
    if not experience_data:
        return 1
    else:
        user_data = get_query(
            f"SELECT users.user_id, users.email, users.username from pt_schema.users "
            f"WHERE users.user_id = '{experience_data[0][1]}'"
        )[0]
        review_data = get_query(
            f"SELECT reviews.review_id, reviews.rev_rating, reviews.comment, "
            f"reviews.user_id, users.email, users.username FROM pt_schema.reviews "
            f"INNER JOIN pt_schema.users ON users.user_id = reviews.user_id "
            f"WHERE users.user_id = '{experience_data[0][1]}'"
        )
        keywords = get_query(f"SELECT keywords.keyword from pt_schema.keywords INNER JOIN "
                             f"pt_schema.experiences_keywords ON "
                             f"keywords.keyword = experiences_keywords.keyword "
                             f"INNER JOIN pt_schema.experiences ON "
                             f"experiences_keywords.exp_id = experiences.exp_id "
                             f"WHERE experiences.exp_id = {exp_id}")
        return experience_data[0], user_data, review_data, keywords


def make_experience(
    user_id,
    name,
    pictures,
    description,
    coords,
    keywords,
    country,
    start="NULL",
    end="NULL",
):
    if get_query(
        f"SELECT exp_id FROM pt_schema.experiences "
        f"WHERE experiences.user_id= '{user_id}' "
        f"AND experiences.title = '{name}' "
        f"AND experiences.description = '{description}'"
    ):
        return 2
    send_query(
        f"INSERT INTO pt_schema.experiences (title, description, latitude, longitude, image, "
        f"user_id, exp_start, exp_end, country) VALUES ('{name}', '{description}',"
        f"{coords['lat']},{coords['lon']},'{pictures}','{user_id}','{start}','{end}','{country}');"
    )
    experience_id = get_query(
        f"SELECT exp_id FROM pt_schema.experiences "
        f"WHERE experiences.user_id= '{user_id}' "
        f"AND experiences.title = '{name}' "
        f"AND experiences.description = '{description}'"
    )[0][0]
    for keyword in keywords:
        send_query(
            f"INSERT INTO pt_schema.experiences_keywords (exp_id, keyword) "
            f"VALUES ('{experience_id}', '{keyword}')"
        )
    return get_experience(experience_id)


def update_experience(
    exp_id,
    user_id,
    name,
    pictures,
    description,
    coords,
    keywords,
    country,
    start="NULL",
    end="NULL",
):
    try:
        user = get_query(f"SELECT user_id from pt_schema.experiences "
                         f"where exp_id = '{exp_id}'")[0][0]
    except KeyError:
        return 1
    if user != user_id:
        return 2
    send_query(
        f"UPDATE pt_schema.experiences SET title = '{name}', description = '{description}' "
        f", latitude = '{coords['lat']}', longitude = '{coords['lon']}', "
        f"image = '{pictures}', user_id = '{user_id}', exp_start = '{start}', "
        f"exp_end = '{end}', country = '{country}' WHERE exp_id = '{exp_id}'"
    )
    send_query(f"DELETE FROM pt_schema.experiences_keywords "
               f"WHERE experiences_keywords.exp_id = '{exp_id}'")
    for keyword in keywords:
        send_query(
            f"INSERT INTO pt_schema.experiences_keywords (exp_id, keyword) "
            f"VALUES ('{exp_id}', '{keyword}')"
        )
    return get_experience(exp_id)


def delete_experience(exp_id):
    if not get_query(
        f"SELECT * FROM pt_schema.experiences WHERE experiences.exp_id = '{exp_id}';"
    ):
        return 1
    else:
        send_query(
            f"DELETE FROM pt_schema.experiences WHERE experiences.exp_id = '{exp_id}';"
        )
        return 0


def get_experiences_by_location(n, s, e, w):
    ids = get_query(f"SELECT exp_id FROM pt_schema.experiences WHERE "
                    f"experiences.longitude BETWEEN {s} AND {n} AND "
                    f"experiences.latitude BETWEEN {w} AND {e}")
    exp_array = []
    for exp_id in ids:
        exp_array.append(get_experience(exp_id[0]))
    return exp_array


def get_experiences_by_user(user_id):
    ids = get_query(f"SELECT exp_id FROM pt_schema.experiences WHERE user_id = '{user_id}'")
    exp_array = []
    for exp_id in ids:
        exp_array.append(get_experience(exp_id[0]))
    return exp_array


def get_review(rev_id):
    response = get_query(
        f"SELECT reviews.review_id, reviews.rev_rating, reviews.comment, "
        f"reviews.user_id, users.email, users.username FROM pt_schema.reviews "
        f"INNER JOIN pt_schema.users ON reviews.user_id = users.user_id "
        f"WHERE reviews.review_id = '{rev_id}';"
    )
    if not response:
        return 1
    else:
        return response


def make_review(user_id, exp_id, stars, review_str):
    if get_query(
        f"SELECT * FROM pt_schema.reviews WHERE reviews.user_id = '{user_id}' AND "
        f"reviews.exp_id = '{exp_id}';"
    ):
        return 1
    send_query(
        f"INSERT INTO pt_schema.reviews (user_id, exp_id, rev_rating, comment) "
        f"VALUES ('{user_id}', '{exp_id}', '{stars}', '{review_str}');"
    )
    return get_query(
        f"SELECT reviews.review_id, reviews.rev_rating, reviews.comment, "
        f"reviews.user_id, users.email, users.username FROM pt_schema.reviews "
        f"INNER JOIN pt_schema.users ON reviews.user_id = users.user_id "
        f"WHERE reviews.user_id = '{user_id}' AND reviews.exp_id = '{exp_id}';"
    )


def update_review(user_id, rev_id, stars, review_str):
    current = get_query(
        f"SELECT reviews.user_id FROM "
        f"pt_schema.reviews WHERE reviews.review_id = '{rev_id}';"
    )
    if not current:
        return 1
    if current[0][0] != user_id:
        return 2
    send_query(
        f"UPDATE pt_schema.reviews SET rev_rating = '{stars}', "
        f"comment = '{review_str}' WHERE reviews.review_id = '{rev_id}';"
    )
    return get_query(
        f"SELECT reviews.review_id, reviews.rev_rating, reviews.comment, "
        f"reviews.user_id, users.email, users.username FROM pt_schema.reviews "
        f"INNER JOIN pt_schema.users ON reviews.user_id = users.user_id "
        f"WHERE reviews.review_id = '{rev_id}';"
    )


def delete_review(rev_id):
    if not get_query(
        f"SELECT * FROM pt_schema.reviews WHERE reviews.review_id = '{rev_id}';"
    ):
        return 1
    else:
        send_query(
            f"DELETE FROM pt_schema.reviews WHERE reviews.review_id = '{rev_id}';"
        )
        return 0


def get_trips_by_user(user_id):
    pass


def get_trip(trip_id):
    trip_data = get_query(
                f"SELECT trips.trip_id, trips.trip_name, trips.trip_start, trips.trip_end "
                f"FROM pt_schema.trips WHERE trips.trip_id = '{trip_id}'")
    itinerary_data = get_query(f"SELECT experiences.exp_id, itineraries.itin_date, itineraries.time"
                               f" FROM pt_schema.experiences "
                               f"INNER JOIN pt_schema.itineraries "
                               f"ON experiences.exp_id = itineraries.exp_id "
                               f"INNER JOIN pt_schema.trips "
                               f"ON itineraries.trip_id = trips.trip_id "
                               f"WHERE trips.trip_id = '{trip_data[0][0]}'")
    user_data = get_query(f"SELECT users.user_id, users.email, users.username "
                          f"FROM pt_schema.users "
                          f"INNER JOIN pt_schema.users_trips "
                          f"ON users.user_id = users_trips.user_id "
                          f"INNER JOIN pt_schema.trips "
                          f"ON users_trips.trip_id = trips.trip_id "
                          f"WHERE trips.trip_id = '{trip_data[0][0]}'")
    return trip_data, itinerary_data, user_data


def make_trip(name, start_date, end_date, experiences, members):
    send_query(f"INSERT INTO pt_schema.trips (trip_name, trip_start, trip_end) "
               f"VALUES ('{name}', '{start_date}','{end_date}')")
    trip_id = get_query(f"SELECT trips.trip_id from pt_schema.trips "
                        f"WHERE trips.trip_name = '{name}' AND "
                        f"trips.trip_start = '{start_date}' AND "
                        f"trips.trip_end = '{end_date}'")[-1][0]
    for member_id in members:
        send_query(f"INSERT INTO pt_schema.users_trips (user_id, trip_id) "
                   f"VALUES ({member_id}, {trip_id})")
    for experience in experiences:
        send_query(f"INSERT INTO pt_schema.itineraries (trip_id, exp_id, itin_date, time) "
                   f"VALUES ({trip_id}, {experience['experienceId']}, "
                   f"'{experience['date']}', '{experience['time']}')")
    return trip_id


def update_trip(trip_id, name, start_date, end_date, experiences, members):
    if not get_query(f"SELECT * from pt_schema.trips WHERE trips.trip_id = {trip_id};"):
        return 1
    send_query(f"UPDATE pt_schema.trips SET trip_name = '{name}', "
               f"trip_start = '{start_date}', trip_end = '{end_date}' "
               f"WHERE trip_id = {trip_id}")
    send_query(f"DELETE FROM pt_schema.users_trips WHERE users_trips.trip_id = '{trip_id}'")
    for member_id in members:
        send_query(f"INSERT INTO pt_schema.users_trips (user_id, trip_id) "
                   f"VALUES ({member_id}, {trip_id})")
    send_query(f"DELETE FROM pt_schema.itineraries WHERE itineraries.trip_id = '{trip_id}'")
    for experience in experiences:
        send_query(f"INSERT INTO pt_schema.itineraries (trip_id, exp_id, itin_date, time) "
                   f"VALUES ({trip_id}, {experience['experienceId']}, "
                   f"'{experience['date']}', '{experience['time']}')")


def delete_trip(trip_id):
    if not get_query(f"SELECT * from pt_schema.trips WHERE trips.trip_id = {trip_id};"):
        return 1
    send_query(f"DELETE FROM pt_schema.trips WHERE trips.trip_id = {trip_id}")


def search_db(location_coords, keywords):
    pass
