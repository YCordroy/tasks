async def get_user(username: str, conn):
    user = await conn.fetchrow(
        "SELECT * FROM users WHERE username = $1",
        username
    )
    return user


async def create_user(username: str, hashed_password: str, conn) -> int:
    user_id = await conn.fetchval(
        """
        INSERT INTO users 
        (username, password_hash)
        VALUES ($1, $2) 
        RETURNING id
        """,
        username,
        hashed_password
    )
    return user_id
