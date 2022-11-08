from database.config import get_query, send_query


def get_trip_ids_by_user(user_id):
    ids = get_query(
        f"SELECT trips.trip_id FROM pt_schema.trips INNER JOIN pt_schema.users_trips "
        f"ON trips.trip_id = users_trips.trip_id "
        f"WHERE users_trips.user_id = '{user_id}'"
    )
    return ids


def get_trip(trip_id):
    trip_data = get_query(
        f"SELECT trips.trip_id, trips.trip_name, trips.trip_start, trips.trip_end "
        f"FROM pt_schema.trips WHERE trips.trip_id = '{trip_id}'"
    )
    itinerary_data = get_query(
        f"SELECT experiences.exp_id, itineraries.itin_date, itineraries.time"
        f" FROM pt_schema.experiences "
        f"INNER JOIN pt_schema.itineraries "
        f"ON experiences.exp_id = itineraries.exp_id "
        f"INNER JOIN pt_schema.trips "
        f"ON itineraries.trip_id = trips.trip_id "
        f"WHERE trips.trip_id = '{trip_data[0][0]}'"
    )
    user_data = get_query(
        f"SELECT users.user_id, users.email, users.username "
        f"FROM pt_schema.users "
        f"INNER JOIN pt_schema.users_trips "
        f"ON users.user_id = users_trips.user_id "
        f"INNER JOIN pt_schema.trips "
        f"ON users_trips.trip_id = trips.trip_id "
        f"WHERE trips.trip_id = '{trip_data[0][0]}'"
    )
    return trip_data, itinerary_data, user_data


def create_trip(name, start_date, end_date, experiences, members):
    send_query(
        f"INSERT INTO pt_schema.trips (trip_name, trip_start, trip_end) "
        f"VALUES ('{name}', '{start_date}','{end_date}')"
    )
    trip_id = get_query(
        f"SELECT trips.trip_id from pt_schema.trips "
        f"WHERE trips.trip_name = '{name}' AND "
        f"trips.trip_start = '{start_date}' AND "
        f"trips.trip_end = '{end_date}'"
    )[-1][0]
    for member_id in members:
        send_query(
            f"INSERT INTO pt_schema.users_trips (user_id, trip_id) "
            f"VALUES ({member_id}, {trip_id})"
        )
    for experience in experiences:
        send_query(
            f"INSERT INTO pt_schema.itineraries (trip_id, exp_id, itin_date, time) "
            f"VALUES ({trip_id}, {experience['experienceId']}, "
            f"'{experience['date']}', '{experience['time']}')"
        )
    return trip_id


def update_trip(trip_id, name, start_date, end_date, experiences, members):
    if not get_query(f"SELECT * from pt_schema.trips WHERE trips.trip_id = {trip_id};"):
        return 1
    send_query(
        f"UPDATE pt_schema.trips SET trip_name = '{name}', "
        f"trip_start = '{start_date}', trip_end = '{end_date}' "
        f"WHERE trip_id = {trip_id}"
    )
    send_query(
        f"DELETE FROM pt_schema.users_trips WHERE users_trips.trip_id = '{trip_id}'"
    )
    for member_id in members:
        send_query(
            f"INSERT INTO pt_schema.users_trips (user_id, trip_id) "
            f"VALUES ({member_id}, {trip_id})"
        )
    send_query(
        f"DELETE FROM pt_schema.itineraries WHERE itineraries.trip_id = '{trip_id}'"
    )
    for experience in experiences:
        send_query(
            f"INSERT INTO pt_schema.itineraries (trip_id, exp_id, itin_date, time) "
            f"VALUES ({trip_id}, {experience['experienceId']}, "
            f"'{experience['date']}', '{experience['time']}')"
        )


def delete_trip(trip_id, token_id):
    members = get_query(
        f"SELECT users_trips.user_id from pt_schema.trips "
        f"INNER JOIN pt_schema.users_trips "
        f"ON users_trips.trip_id = trips.trip_id "
        f"WHERE trips.trip_id = {trip_id};"
    )
    if not members:
        return 1
    for i in range(len(members)):
        members[i] = members[i][0]
    if int(token_id) not in members:
        return 2
    send_query(f"DELETE FROM pt_schema.trips WHERE trips.trip_id = {trip_id}")
