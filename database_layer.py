import psycopg2 as db
import credentials

# Information on psycopg2 library from
# https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries
# 10/12/2022


def connect_to_database():
    """Connects to the database associated with the information given in the
    credentials.py file."""
    connection = db.connect(host=credentials.host,
                            database=credentials.database,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)

    cur = connection.cursor()
    return connection, cur


def get_query(query):
    """Takes in a query string and returns the result of running that SQL
    query for the database."""
    connection, cursor = connect_to_database()
    cursor.execute(query)
    return cursor.fetchall()


def send_query(query):
    """Takes in a query string. Modifies the database by running the SQL query.
    Does not return anything."""
    connection, cursor = connect_to_database()
    cursor.execute(query)
    connection.commit()


def register_user(username, password_hash, email):
    if get_query(f"SELECT * FROM pt_schema.users WHERE email = '{email}';"):
        return 1
    else:
        send_query("INSERT INTO pt_schema.users (username, password, email) "
                   f"VALUES ('{username}', '{password_hash}', '{email}');")
        user_id = get_query(f"SELECT users.user_id FROM pt_schema.users WHERE email = '{email}';")[0][0]
        return user_id, email, username


def login_user(email, password):
    if not get_query(f"SELECT * FROM pt_schema.users "
                     f"WHERE users.email = '{email}' AND users.password = '{password}'"):
        return 1
    else:
        user_id, username = get_query(f"SELECT user_id, username FROM pt_schema.users WHERE email = '{email}'")[0]
        return user_id, email, username


def get_experience(exp_id):
    experience_data = get_query(f"SELECT experiences.exp_id, experiences.user_id, experiences.title, "
                                f"experiences.description, experiences.latitude, experiences.longitude, "
                                f"experiences.exp_start, experiences.exp_end, experiences.image, "
                                f"experiences.country FROM pt_schema.experiences "
                                f"WHERE experiences.exp_id = '{exp_id}'")
    if not experience_data:
        return 1
    else:
        user_data = get_query(f"SELECT users.user_id, users.email, users.username from pt_schema.users "
                              f"WHERE users.user_id = '{experience_data[0][1]}'")[0]
        review_data = get_query(f"SELECT reviews.review_id, reviews.rev_rating, reviews.comment, "
                                f"reviews.user_id, users.email, users.username FROM pt_schema.reviews "
                                f"INNER JOIN pt_schema.users ON users.user_id = reviews.user_id "
                                f"WHERE users.user_id = '{experience_data[0][1]}'")
        return experience_data[0], user_data, review_data


def make_experience(user_id, name, pictures, description, coords, keywords, country, start="NULL", end="NULL"):
    if get_query(f"SELECT exp_id FROM pt_schema.experiences "
                 f"WHERE experiences.user_id= '{user_id}' "
                 f"AND experiences.title = '{name}' "
                 f"AND experiences.description = '{description}'"):
        return 2
    send_query(f"INSERT INTO pt_schema.experiences (title, description, latitude, longitude, image, "
               f"user_id, exp_start, exp_end, country) VALUES ('{name}', '{description}',"
               f"'{coords['lat']}','{coords['lon']}','{pictures}','{user_id}','{start}','{end}','{country}');")
    experience_id = get_query(f"SELECT exp_id FROM pt_schema.experiences "
                              f"WHERE experiences.user_id= '{user_id}' "
                              f"AND experiences.title = '{name}' "
                              f"AND experiences.description = '{description}'")
    return get_experience(experience_id[0][0])


def update_experience(exp_id, user_id, name, pictures, description, coords, keywords, country, start="NULL", end="NULL"):
    user = get_query(f"SELECT user_id from pt_schema.experiences where exp_id = '{exp_id}'")[0][0]
    if not user:
        return 1
    if user != user_id:
        return 2
    send_query(f"UPDATE pt_schema.experiences SET title = '{name}', description = '{description}' "
               f", latitude = '{coords['lat']}', longitude = '{coords['lon']}', "
               f"image = '{pictures}', user_id = '{user_id}', exp_start = '{start}', "
               f"exp_end = '{end}', country = '{country}' WHERE exp_id = '{exp_id}'")
    experience_id = get_query(f"SELECT experiences.exp_id FROM pt_schema.experiences "
                              f"WHERE experiences.user_id= '{user_id}' "
                              f"AND experiences.title = '{name}' "
                              f"AND experiences.description = '{description}'")
    return get_experience(experience_id[0][0])


def delete_experience(exp_id):
    if not get_query(f"SELECT * FROM pt_schema.experiences WHERE experiences.exp_id = '{exp_id}';"):
        return 1
    else:
        send_query(f"DELETE FROM pt_schema.experiences WHERE experiences.exp_id = '{exp_id}';")
        return 0


def get_review(rev_id):
    response = get_query(f"SELECT reviews.review_id, reviews.rev_rating, reviews.comment, "
                         f"reviews.user_id, users.email, users.username FROM pt_schema.reviews "
                         f"INNER JOIN pt_schema.users ON reviews.user_id = users.user_id "
                         f"WHERE reviews.review_id = '{rev_id}';")
    if not response:
        return 1
    else:
        return response


def make_review(user_id, exp_id, stars, review_str):
    if get_query(f"SELECT * FROM pt_schema.reviews WHERE reviews.user_id = '{user_id}' AND "
                 f"reviews.exp_id = '{exp_id}';"):
        return 1
    send_query(f"INSERT INTO pt_schema.reviews (user_id, exp_id, rev_rating, comment) "
               f"VALUES ('{user_id}', '{exp_id}', '{stars}', '{review_str}');")
    return get_query(f"SELECT reviews.review_id, reviews.rev_rating, reviews.comment, "
                     f"reviews.user_id, users.email, users.username FROM pt_schema.reviews "
                     f"INNER JOIN pt_schema.users ON reviews.user_id = users.user_id "
                     f"WHERE reviews.user_id = '{user_id}' AND reviews.exp_id = '{exp_id}';")


def update_review(user_id, rev_id, stars, review_str):
    current = get_query(f"SELECT reviews.user_id FROM "
                        f"pt_schema.reviews WHERE reviews.review_id = '{rev_id}';")
    if not current:
        return 1
    if current[0][0] != user_id:
        return 2
    send_query(f"UPDATE pt_schema.reviews SET rev_rating = '{stars}', "
               f"comment = '{review_str}' WHERE reviews.review_id = '{rev_id}';")
    return get_query(f"SELECT reviews.review_id, reviews.rev_rating, reviews.comment, "
                     f"reviews.user_id, users.email, users.username FROM pt_schema.reviews "
                     f"INNER JOIN pt_schema.users ON reviews.user_id = users.user_id "
                     f"WHERE reviews.review_id = '{rev_id}';")


def delete_review(rev_id):
    if not get_query(f"SELECT * FROM pt_schema.reviews WHERE reviews.review_id = '{rev_id}';"):
        return 1
    else:
        send_query(f"DELETE FROM pt_schema.reviews WHERE reviews.review_id = '{rev_id}';")
        return 0


def get_trips_by_user(user_id):
    pass


def get_experiences_by_user(user_id):
    pass


def pack_trip(trip):
    pass


def get_trip(trip_id):
    pass


def make_trip(name, start_date, end_date, experiences, members):
    pass


def update_trip(trip_id, name, start_date, end_date, experiences, members):
    pass


def delete_trip(trip_id):
    pass


def search_db(location_coords, keywords):
    pass