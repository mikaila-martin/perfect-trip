from database.config import query_one


def get_user_by_id(user_id):
    user = query_one(
        """
        SELECT * FROM pt_schema.users WHERE users.user_id = %s
        """,
        (user_id,),
    )

    if user is None:
        raise Exception("User not found.")

    return user
