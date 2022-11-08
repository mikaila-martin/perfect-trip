from database.config import get_query, send_query


def register_user(email, username, password_hash):

    user = get_query(
        """
        SELECT * FROM pt_schema.users WHERE email = %s;
        """,
        (email,),
    )

    if user:
        raise Exception("Email in use.")

    send_query(
        """
        INSERT INTO pt_schema.users (email, username, password) 
        VALUES (%s, %s, %s);
        """,
        (email, username, password_hash),
    )

    new_user = get_query(
        """
        SELECT user_id, username, avatar FROM pt_schema.users WHERE email = %s;
        """,
        (email,),
    )

    return new_user[0]


def login_user(email, password_hash):

    user = get_query(
        """
        SELECT * FROM pt_schema.users 
        WHERE users.email = %s AND users.password = %s
        """,
        (email, password_hash),
    )

    if user is None:
        raise Exception("Username or password incorrect.")

    return user[0]
