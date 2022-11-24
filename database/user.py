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


def update_username_db(user_id, username):
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


def delete_account_db(user_id):
    send_query("""DELETE FROM pt_schema.users WHERE users.user_id = %s; """, (user_id,))


def get_avatar_by_user(user_id):
    avatar = get_by_id(user_id)["avatar"]
    return avatar


def update_avatar_db(user_id, avatar):
    send_query("""UPDATE pt_schema.users SET avatar = %s
         WHERE user_id = %s;""", (avatar, user_id))
    return get_by_id(user_id)
