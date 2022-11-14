from database.connection import get_query, send_query


def get_review(rev_id):
    response = get_query(
        f"SELECT reviews.review_id, reviews.rev_rating, reviews.comment, "
        f"reviews.user_id, users.email, users.username FROM pt_schema.reviews "
        f"INNER JOIN pt_schema.users ON reviews.user_id = users.user_id "
        f"WHERE reviews.review_id = '{rev_id}';"
    )
    if not response:
        raise Exception("Review not found.")
    return response


def create_review(user_id, exp_id, stars, review_str):
    # Check if review exists
    if get_query(
        f"SELECT * FROM pt_schema.reviews WHERE reviews.user_id = '{user_id}' AND "
        f"reviews.exp_id = '{exp_id}';"
    ):
        raise Exception("Review already exists.")
    # Create review
    send_query(
        f"INSERT INTO pt_schema.reviews (user_id, exp_id, rev_rating, comment) "
        f"VALUES ('{user_id}', '{exp_id}', '{stars}', '{review_str}');"
    )
    # Get review
    return get_query(
        f"SELECT reviews.review_id, reviews.rev_rating, reviews.comment, "
        f"reviews.user_id, users.email, users.username FROM pt_schema.reviews "
        f"INNER JOIN pt_schema.users ON reviews.user_id = users.user_id "
        f"WHERE reviews.user_id = '{user_id}' AND reviews.exp_id = '{exp_id}';"
    )


def update_review(user_id, rev_id, stars, review_str):
    # Check if review exists
    current = get_query(
        f"SELECT reviews.user_id FROM "
        f"pt_schema.reviews WHERE reviews.review_id = '{rev_id}';"
    )
    if not current:
        raise Exception("Review does not exist.")
    if current[0]["user_id"] != user_id:
        raise Exception("Review does not belong to this user.")
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


def delete_review(token_id, rev_id):
    try:
        user_id = get_query(
            f"SELECT reviews.user_id FROM pt_schema.reviews "
            f"WHERE reviews.review_id = %s;", rev_id
        )[0]["user_id"]
    except TypeError and KeyError:
        raise Exception("Review not found")
    if token_id != user_id:
        raise Exception("Review does not belong to this user")
    else:
        send_query(
            f"DELETE FROM pt_schema.reviews WHERE reviews.review_id = '{rev_id}';"
        )
        return "Successfully Deleted."
