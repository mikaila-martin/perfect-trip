from database.connection import get_query, send_query


def get_review(rev_id):
    response = get_query(
        """SELECT reviews.review_id, reviews.rev_rating, reviews.comment, 
        reviews.user_id, users.email, users.username FROM pt_schema.reviews 
        INNER JOIN pt_schema.users ON reviews.user_id = users.user_id 
        WHERE reviews.review_id = %s;""", (rev_id,)
    )
    if not response:
        raise Exception("Review not found.")
    return response


def create_review(user_id, exp_id, stars, review_str):
    # Check if review exists
    if get_query(
        """SELECT * FROM pt_schema.reviews WHERE reviews.user_id = %s AND 
        reviews.exp_id = %s;""", (user_id, exp_id)
    ):
        raise Exception("Review already exists.")
    # Create review
    send_query(
        """INSERT INTO pt_schema.reviews (user_id, exp_id, rev_rating, comment) 
        VALUES (%s, %s, %s, %s);""", (user_id, exp_id, stars, review_str)
    )
    # Get review
    return get_query(
        """SELECT reviews.review_id, reviews.rev_rating, reviews.comment, 
        reviews.user_id, users.email, users.username FROM pt_schema.reviews 
        INNER JOIN pt_schema.users ON reviews.user_id = users.user_id 
        WHERE reviews.user_id = %s AND reviews.exp_id = %s;""", (user_id, exp_id)
    )


def update_review(user_id, rev_id, stars, review_str):
    # Check if review exists
    current = get_query(
        """SELECT reviews.user_id FROM 
        pt_schema.reviews WHERE reviews.review_id = %s;""", (rev_id,)
    )
    if not current:
        raise Exception("Review does not exist.")
    if current[0]["user_id"] != user_id:
        raise Exception("Review does not belong to this user.")
    send_query(
        """UPDATE pt_schema.reviews SET rev_rating = %s, 
        comment = %s WHERE reviews.review_id = %s;""", (stars, review_str, rev_id)
    )
    return get_query(
        """SELECT reviews.review_id, reviews.rev_rating, reviews.comment, 
        reviews.user_id, users.email, users.username FROM pt_schema.reviews 
        INNER JOIN pt_schema.users ON reviews.user_id = users.user_id 
        WHERE reviews.review_id = %s;""", (rev_id,)
    )


def delete_review(token_id, rev_id):
    try:
        user_id = get_query(
            """SELECT reviews.user_id FROM pt_schema.reviews 
            WHERE reviews.review_id = %s;""", (rev_id,)
        )[0]["user_id"]
    except TypeError and KeyError:
        raise Exception("Review not found")
    if token_id != user_id:
        raise Exception("Review does not belong to this user")
    else:
        send_query(
            """DELETE FROM pt_schema.reviews WHERE reviews.review_id = %s;""", (rev_id,)
        )
        return "Successfully Deleted."
