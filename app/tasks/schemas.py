from pydantic import BaseModel
from typing import Optional, Literal


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Literal['В процессе', 'Завершена'] = 'В процессе'


class Task(TaskCreate):
    id: int
