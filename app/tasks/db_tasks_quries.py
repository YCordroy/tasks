from typing import Optional

from tasks.schemas import TaskCreate


async def get_user(username: str, conn):
    user = await conn.fetchrow(
        "SELECT * FROM users WHERE username = $1",
        username
    )
    return user


async def create_task(data, user, conn):
    task_id = await conn.fetchval(
        """
        INSERT INTO tasks
        (title, description, status, user_id) 
        VALUES 
        ($1, $2, $3, $4)
        RETURNING id
        """,
        data.title,
        data.description,
        data.status,
        user['id']
    )
    return task_id


async def edit_task(data: TaskCreate, task_id: int, conn):
    await conn.execute(
        """
        UPDATE tasks 
        SET title = $1, description = $2, status = $3 
        WHERE id = $4
        """,
        data.title,
        data.description,
        data.status,
        task_id
    )


async def get_task(task_id: int, conn):
    task = await conn.fetchrow("SELECT * FROM tasks WHERE id = $1", task_id)
    return task


async def get_tasks(username: str, conn, status: Optional[str] = None):
    params = [username]
    query = """
        SELECT * 
        FROM tasks 
        WHERE user_id = 
        (SELECT id FROM users WHERE username = $1)
        """
    if status:
        query += " AND status = $2"
        params.append(status)

    return await conn.fetch(
        query,
        *params
    )


async def delete_task(task_id: int, conn):
    await conn.execute("DELETE FROM tasks WHERE id = $1", task_id)
