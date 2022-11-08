from database.config import query_one, mutation


def register_user(email, username, password_hash):

    existing_user = query_one(
        """
        SELECT user_id FROM pt_schema.users WHERE email = %s;
        """,
        (email,),
    )

    if existing_user:
        raise Exception("Email in use.")

    mutation(
        """
        INSERT INTO pt_schema.users (email, username, password) 
        VALUES (%s, %s, %s);
        """,
        (email, username, password_hash),
    )

    new_user = query_one(
        """
        SELECT user_id, username, avatar FROM pt_schema.users 
        WHERE email = %s;
        """,
        (email,),
    )

    return new_user


def login_user(email, password_hash):

    existing_user = query_one(
        """
        SELECT user_id, username, avatar FROM pt_schema.users 
        WHERE users.email = %s AND users.password = %s
        """,
        (email, password_hash),
    )

    if existing_user is None:
        raise Exception("Username or password incorrect.")

    return existing_user
