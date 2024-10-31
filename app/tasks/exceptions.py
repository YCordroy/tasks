from fastapi import HTTPException, status

auth_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token",
    headers={"WWW-Authenticate": "Bearer"},
)

task_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Task not found"
)