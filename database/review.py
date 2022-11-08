from database.connection import get_query, send_query


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


def create_review(user_id, exp_id, stars, review_str):
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


def delete_review(rev_id, token_id):
    user_id = get_query(
        f"SELECT reviews.user_id FROM pt_schema.reviews "
        f"WHERE reviews.review_id = '{rev_id}';"
    )[0][0]
    if not user_id:
        return 1
    if int(token_id) != user_id:
        return 2
    else:
        send_query(
            f"DELETE FROM pt_schema.reviews WHERE reviews.review_id = '{rev_id}';"
        )
        return 0
