from database.connection import get_query, send_query


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


def update_username(user_id, username):
    send_query("""UPDATE pt_schema.users SET username = %s
     WHERE user_id = %s;""", (username, user_id))
    return get_by_id(user_id)


def update_password_db(user_id, password):
    send_query("""UPDATE pt_schema.users SET password = %s
         WHERE user_id = %s;""", (password, user_id))


def check_password(user_id, password_hash):
    if not get_query("""SELECT * FROM pt_schema.users 
    WHERE users.user_id = %s AND users.password = %s;""", (user_id, password_hash)):
        raise Exception("Password is incorrect.")
    return
