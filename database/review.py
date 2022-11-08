from database.config import query, mutation
from util import pack_reviews


def get_review_by_id(review_id):

    review = query(
        """
        SELECT reviews.review_id, reviews.rev_rating, reviews.comment, 
        reviews.user_id, users.email, users.username FROM pt_schema.reviews 
        INNER JOIN pt_schema.users ON reviews.user_id = users.user_id 
        WHERE reviews.review_id = %s;
        """,
        (review_id,),
    )

    if review is None:
        raise Exception("Review not found.")

    return pack_reviews([review])[0]


def create_review(review):

    existing_review = query(
        """
        SELECT reviews.review_id FROM pt_schema.reviews 
        WHERE reviews.user_id = %s AND reviews.exp_id = %s
        """,
        (review["user_id"], review["exp_id"]),
    )

    if existing_review:
        raise Exception("Only one review per experience allowed.")

    mutation(
        """
        INSERT INTO pt_schema.reviews (user_id, exp_id, rev_rating, comment) 
        VALUES (%s, %s, %s, %s);
        """,
        (review["user_id"], review["exp_id"], review["rating"], review["comment"]),
    )

    review = query(
        """
        SELECT reviews.review_id, reviews.rev_rating, reviews.comment, 
        reviews.user_id, users.email, users.username FROM pt_schema.reviews 
        INNER JOIN pt_schema.users ON reviews.user_id = users.user_id 
        WHERE reviews.user_id = %s AND reviews.exp_id = %s;
        """,
        (review["user_id"], review["exp_id"]),
    )

    return pack_reviews([review])[0]


def update_review(review):

    existing_review = query(
        """
        SELECT reviews.review_id FROM pt_schema.reviews 
        WHERE reviews.review_id = %s;
        """,
        (review["review_id"],),
    )

    if existing_review is None:
        raise Exception("Review not found.")

    mutation(
        """
        UPDATE pt_schema.reviews SET rev_rating = %s, comment = %s 
        WHERE reviews.review_id = %s;
        """,
        (review["rating"], review["comment"], review["review_id"]),
    )

    review = query(
        """
        SELECT reviews.review_id, reviews.rev_rating, reviews.comment, 
        reviews.user_id, users.email, users.username FROM pt_schema.reviews 
        INNER JOIN pt_schema.users ON reviews.user_id = users.user_id 
        WHERE reviews.review_id = %s;
        """,
        (review["review_id"],),
    )

    return pack_reviews([review])[0]


def delete_review(review_id):

    existing_review = query(
        """
        SELECT reviews.review_id FROM pt_schema.reviews 
        WHERE reviews.review_id = %s;
        """,
        (review_id,),
    )

    if existing_review is None:
        raise Exception("Review not found.")

    mutation(
        """
        DELETE FROM pt_schema.reviews WHERE reviews.review_id = %s;
        """,
        (review_id,),
    )
