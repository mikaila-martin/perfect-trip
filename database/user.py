from database.connection import get_query


def get_by_id(user_id):
    user = get_query(
        """
        SELECT * FROM pt_schema.users WHERE users.user_id = %s
        """,
        (user_id,),
    )

    if user:
        return user[0]

    else:
        raise Exception("User not found.")
