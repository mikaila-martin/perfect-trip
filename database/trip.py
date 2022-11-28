from util import is_valid_uuid, get_date_string, get_time_string
from database.connection import get_query, send_query
from database.experience import get_experience_by_id
from services.google import places_details


def get_trip_ids_by_user(user_id):

    # Get IDs
    ids = get_query(
        """SELECT trips.trip_id FROM pt_schema.trips INNER JOIN pt_schema.users_trips 
        ON trips.trip_id = users_trips.trip_id 
        WHERE users_trips.user_id = %s""",
        (user_id,),
    )

    return ids


def get_trip(trip_id):

    # Get trip data
    trip_data = get_query(
        """
        SELECT trips.trip_id, trips.name, trips.start_date, trips.end_date 
        FROM pt_schema.trips WHERE trips.trip_id = %s;
        """,
        (trip_id,),
    )

    # Check to see if trip exists
    if trip_data is None:
        raise Exception("Trip not found.")
    else:
        trip_data = trip_data[0]

    # Get itinerary data
    itinerary_data = get_query(
        """
        SELECT * FROM pt_schema.itineraries
        WHERE itineraries.trip_id = %s;
        """,
        (trip_id,),
    )

    itinerary = []

    for event in itinerary_data:

        experience = None

        # Get experience from database
        if is_valid_uuid(event["exp_id"]):
            experience = get_experience_by_id(event["exp_id"])

        # Get experience from google
        else:
            experience = places_details(event["exp_id"])

        # If the experience was found, add it to the itinerary
        if experience is not None:
            itinerary.append(
                {
                    "id": event["itin_id"],
                    "index": event["index"],
                    "experience": experience,
                    "date": get_date_string(event["date"]),
                    "time": {
                        "start": get_time_string(event["start_time"]),
                        "end": get_time_string(event["end_time"]),
                    },
                }
            )

    # Calculate initial coordinates
    latitude_sum = 0
    longitude_sum = 0

    for event in itinerary:
        latitude_sum += event["experience"]["latitude"]
        longitude_sum += event["experience"]["longitude"]

    initial_coordinates = {
        "center": {
            "latitude": round(latitude_sum / len(itinerary), 4),
            "longitude": round(longitude_sum / len(itinerary), 4),
        },
        "northEast": None,
        "southWest": None,
    }

    # Get member data
    member_data = get_query(
        """
        SELECT users.user_id, users.username, users.avatar 
        FROM pt_schema.users 
        INNER JOIN pt_schema.users_trips 
        ON users.user_id = users_trips.user_id 
        INNER JOIN pt_schema.trips 
        ON users_trips.trip_id = trips.trip_id 
        WHERE trips.trip_id = %s;
        """,
        (trip_id,),
    )

    members = []

    for member in member_data:
        members.append(
            {
                "userId": member["user_id"],
                "username": member["username"],
                "avatar": member["avatar"],
            }
        )

    # Build trip object
    trip = {
        "id": trip_data["trip_id"],
        "name": trip_data["name"],
        "startDate": get_date_string(trip_data["start_date"]),
        "endDate": get_date_string(trip_data["end_date"]),
        "initialCoordinates": initial_coordinates,
        "itinerary": itinerary,
        "members": members,
    }

    return trip


def create_trip(name, start_date, end_date, itinerary, members):

    # Create trip
    send_query(
        """
        INSERT INTO pt_schema.trips (name, start_date, end_date) 
        VALUES (%s, %s, %s)
        """,
        (name, start_date, end_date),
    )

    # Get trip id
    trip_id = get_query(
        """
        SELECT trips.trip_id from pt_schema.trips 
        WHERE trips.name = %s AND 
        trips.start_date = %s AND 
        trips.end_date = %s
        """,
        (name, start_date, end_date),
    )[-1]["trip_id"]

    # Create trip members
    for member in members:
        send_query(
            """
            INSERT INTO pt_schema.users_trips (user_id, trip_id) 
            VALUES (%s, %s)
            """,
            (member["userId"], trip_id),
        )

    # Create trip itinerary
    for event in itinerary:
        send_query(
            """
            INSERT INTO pt_schema.itineraries (trip_id, exp_id, index, date, start_time, end_time) 
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (
                trip_id,
                event["experience"]["id"],
                event["index"],
                event["date"],
                event["time"]["start"],
                event["time"]["end"],
            ),
        )

    return get_trip(trip_id)


def update_trip(trip_id, name, start_date, end_date, itinerary, members):

    # Update trip
    send_query(
        """
        UPDATE pt_schema.trips SET name = %s, start_date = %s, end_date = %s 
        WHERE trip_id = %s;
        """,
        (name, start_date, end_date, trip_id),
    )

    # Delete old members
    send_query(
        """
        DELETE FROM pt_schema.users_trips
        WHERE users_trips.trip_id = %s
        """,
        (trip_id,),
    )

    # Create new members
    for member in members:
        send_query(
            """
            INSERT INTO pt_schema.users_trips (user_id, trip_id) 
            VALUES (%s, %s)
            """,
            (member["userId"], trip_id),
        )

    # Delete old itinerary
    send_query(
        """
        DELETE FROM pt_schema.itineraries WHERE itineraries.trip_id = %s
        """,
        (trip_id,),
    )

    # Create new itinerary
    for event in itinerary:
        send_query(
            """
            INSERT INTO pt_schema.itineraries (trip_id, exp_id, index, date, start_time, end_time) 
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (
                trip_id,
                event["experience"]["id"],
                event["index"],
                event["date"],
                event["time"]["start"],
                event["time"]["end"],
            ),
        )

    return get_trip(trip_id)


def delete_trip(trip_id):

    # Delete the trip
    send_query(
        """
        DELETE FROM pt_schema.trips WHERE trips.trip_id = %s;
        """,
        (trip_id,),
    )
