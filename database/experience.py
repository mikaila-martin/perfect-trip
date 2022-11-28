from database.connection import get_query, send_query
from util import pack_experience


def search_experiences(n, s, e, w, keyword_array):
    experiences = get_query(
        f"SELECT experiences.exp_id, experiences_keywords.keyword "
        f"FROM pt_schema.experiences "
        f"INNER JOIN pt_schema.experiences_keywords "
        f"ON experiences.exp_id = experiences_keywords.exp_id "
        f"WHERE "
        f"experiences.longitude BETWEEN {w} AND {e} AND "
        f"experiences.latitude BETWEEN {s} AND {n}"
    )

    if experiences is None:
        return []

    id_array = []
    exp_array = []

    try:
        for exp in experiences:
            if (
                exp["keyword"] in keyword_array
                and exp["exp_id"] not in id_array
                or keyword_array == []
            ):
                id_array.append(exp["exp_id"])
        for id in id_array:
            exp_array.append(get_experience_by_id(id))
    except TypeError:
        pass

    return exp_array


def get_experience_by_id(exp_id):

    # Get experience
    experience = get_query(
        """
        SELECT experiences.exp_id, experiences.user_id, experiences.title, 
        experiences.description, experiences.latitude, experiences.longitude, 
        experiences.images, experiences.country_name, experiences.country_code
        FROM pt_schema.experiences 
        WHERE experiences.exp_id = %s
        """,
        (exp_id,),
    )

    if experience is None:
        raise Exception("Experience not found.")

    experience = experience[0]
    user_id = experience["user_id"]

    # Get user
    user = get_query(
        """
        SELECT users.user_id, users.username, users.avatar from pt_schema.users 
        WHERE users.user_id = %s
        """,
        (user_id,),
    )[0]

    # Get reviews
    reviews = get_query(
        """
        SELECT reviews.review_id, reviews.rev_rating, reviews.comment, 
        reviews.user_id, users.avatar, users.username FROM pt_schema.reviews 
        INNER JOIN pt_schema.users ON users.user_id = reviews.user_id 
        WHERE users.user_id = %s
        """,
        (user_id,),
    )

    # Get keywords
    keywords = get_query(
        """
        SELECT keywords.keyword from pt_schema.keywords INNER JOIN 
        pt_schema.experiences_keywords ON 
        keywords.keyword = experiences_keywords.keyword 
        INNER JOIN pt_schema.experiences ON 
        experiences_keywords.exp_id = experiences.exp_id 
        WHERE experiences.exp_id = %s
        """,
        (exp_id,),
    )

    return pack_experience(experience, user, reviews, keywords)


def get_experiences_by_user_id(user_id):

    # Get experience id's
    experiences = get_query(
        """
        SELECT exp_id FROM pt_schema.experiences WHERE user_id = %s
        """,
        (user_id,),
    )

    # Get experiences
    user_experiences = []

    for experience in experiences:
        user_experiences.append(get_experience_by_id(experience["exp_id"]))

    return user_experiences


def create_experience(experience):

    # Check to see if the experience already exists
    existing_experience = get_query(
        """
        SELECT exp_id FROM pt_schema.experiences
        WHERE experiences.user_id = %s
        AND experiences.title = %s
        AND experiences.description = %s
        """,
        (experience["user_id"], experience["title"], experience["description"]),
    )

    if existing_experience:
        raise Exception("Experience already exists.")

    # Create the experience
    send_query(
        """
        INSERT INTO pt_schema.experiences (user_id, title, description, latitude,
        longitude, country_name, country_code, images)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            experience["user_id"],
            experience["title"],
            experience["description"],
            experience["latitude"],
            experience["longitude"],
            experience["country_name"],
            experience["country_code"],
            experience["images"],
        ),
    )

    # Fetch the experience id
    exp_id = get_query(
        """
        SELECT exp_id FROM pt_schema.experiences
        WHERE experiences.user_id = %s 
        AND experiences.title = %s
        AND experiences.description = %s
        """,
        (
            experience["user_id"],
            experience["title"],
            experience["description"],
        ),
    )[0]["exp_id"]

    # Create the experience keywords
    for keyword in experience["keywords"]:
        send_query(
            """
            INSERT INTO pt_schema.experiences_keywords (exp_id, keyword)
            VALUES (%s, %s)
            """,
            (exp_id, keyword),
        )

    # Return the formatted experience
    return get_experience_by_id(exp_id)


def update_experience(experience):

    # Check to see if the experience already exists
    existing_experience = get_query(
        """
        SELECT user_id FROM pt_schema.experiences
        WHERE experiences.exp_id = %s
        """,
        (experience["exp_id"]),
    )

    if existing_experience is None:
        raise Exception("Experience not found.")

    if existing_experience[0]["user_id"] != experience["user_id"]:
        raise Exception("Experience cannot be deleted.")

    # Update the experience
    send_query(
        """
        UPDATE pt_schema.experiences SET title = %s, description = %s, 
        latitude = %s, longitude = %s, images = %s, user_id = %s, 
        country = %s WHERE exp_id = %s
        """,
        (
            experience["title"],
            experience["description"],
            experience["latitude"],
            experience["longitude"],
            experience["images"],
            experience["user_id"],
            experience["country"],
            experience["exp_id"],
        ),
    )

    # Overwrite keywords
    send_query(
        """
        DELETE FROM pt_schema.experiences_keywords 
        WHERE experiences_keywords.exp_id = %s
        """,
        (experience["exp_id"],),
    )

    for keyword in experience["keywords"]:
        send_query(
            """
            INSERT INTO pt_schema.experiences_keywords (exp_id, keyword) 
            VALUES (%s, %s)
            """,
            (experience["exp_id"], keyword),
        )

    return get_experience_by_id(experience["exp_id"])


def delete_experience(user_id, exp_id):

    # Check to see if the experience already exists
    existing_experience = get_query(
        """
        SELECT user_id FROM pt_schema.experiences 
        WHERE experiences.exp_id = %s
        """,
        exp_id,
    )

    if existing_experience is None:
        raise Exception("Experience not found.")

    if existing_experience[0]["user_id"] != user_id:
        raise Exception("Experience cannot be deleted.")

    # Delete the experience
    send_query(
        """
        DELETE FROM pt_schema.experiences WHERE experiences.exp_id = %s;
        """,
        (exp_id,),
    )


def get_images(exp_id):

    # Get images
    images = get_query(
        """
        SELECT experiences.images FROM pt_schema.experiences 
        WHERE experiences.exp_id = %s
        """,
        (exp_id,),
    )

    return images[0]["images"]
