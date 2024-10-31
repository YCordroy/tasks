from typing import List, Optional, Literal

from fastapi import Depends, HTTPException, status, APIRouter, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from config.settings import SECRET_KEY, ALGORITHM
from config.db_config import get_db
import tasks.db_tasks_quries as query
from tasks.schemas import TaskCreate, Task
from tasks.exceptions import auth_exception, task_exception

router_task = APIRouter()
bearer_scheme = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    """Получение пользователя из токена"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise auth_exception
        return username
    except JWTError:
        raise auth_exception


async def check_user(task, current_user, conn):
    """Проверка, что пользователь является автором"""
    user = await query.get_user(current_user, conn)
    if task['user_id'] != user['id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this task")


@router_task.post('/tasks/', response_model=Task)
async def create_task(
        data: TaskCreate,
        current_user: str = Depends(get_current_user),
        conn=Depends(get_db)
) -> Task:
    """Создание задачи"""
    user = await query.get_user(current_user, conn)
    task_id = await query.create_task(data, user, conn)

    return Task(id=task_id, user_id=user['id'], **data.dict())


@router_task.get('/tasks/', response_model=List[Task])
async def get_tasks(
        status: Optional[Literal["В процессе", "Завершена"]] = Query(None),
        current_user: str = Depends(get_current_user),
        conn=Depends(get_db)
) -> List[Task]:
    """Получение списка задач"""
    tasks = await query.get_tasks(current_user, conn=conn, status=status)

    return [
        Task(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            status=row['status']
        ) for row in tasks
    ]


@router_task.get('/tasks/{task_id}', response_model=Task)
async def get_task(
        task_id: int,
        current_user: str = Depends(get_current_user),
        conn=Depends(get_db)
) -> Task:
    """Получение отдельной задачи"""
    task = await query.get_task(task_id, conn)

    if task is None:
        raise task_exception

    await check_user(task, current_user, conn)

    return Task(
        id=task['id'],
        title=task['title'],
        description=task['description'],
        status=task['status']
    )


@router_task.put('/tasks/{task_id}', response_model=Task)
async def update_task(
        task_id: int,
        data: TaskCreate,
        current_user: str = Depends(get_current_user),
        conn=Depends(get_db)
) -> Task:
    """Обновление задачи"""
    task_to_update = await query.get_task(task_id, conn)
    if task_to_update is None:
        raise task_exception
    await check_user(task_to_update, current_user, conn)
    await query.edit_task(data, task_id, conn)

    return Task(
        id=task_id,
        **data.dict()
    )


@router_task.delete('/tasks/{task_id}')
async def delete_task(
        task_id: int,
        current_user: str = Depends(get_current_user),
        conn=Depends(get_db)
) -> dict:
    """Удаление задачи"""
    task_to_delete = await query.get_task(task_id, conn)
    if task_to_delete is None:
        raise task_exception
    await check_user(task_to_delete, current_user, conn)
    await query.delete_task(task_id, conn)
    return {"data": "Task deleted successfully"}
