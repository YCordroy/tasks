import asyncpg

from .settings import app, PASSWORD, USER, DATABASE


@app.on_event("startup")
async def startup():
    app.state.pool = await asyncpg.create_pool(
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        host='db'
    )
    await init_db()


@app.on_event("shutdown")
async def shutdown():
    await app.state.pool.close()


async def get_db():
    async with app.state.pool.acquire() as conn:
        yield conn


async def init_db():
    conn = await app.state.pool.acquire()
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
        );
    """)
