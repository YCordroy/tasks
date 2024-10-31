from datetime import datetime, timedelta

import bcrypt
import redis
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from config.db_config import get_db
from auth.schemas import User, UserCreate, Token, TokenRefreshRequest
import auth.db_auth_queries as query
from config.settings import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM
from auth.exceptions import auth_exception

router_auth = APIRouter()

bearer_scheme = HTTPBearer()

redis_client = redis.Redis(host='redis', port=6379, db=0)


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Создание токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router_auth.post('/auth/register', response_model=User)
async def registration(data: UserCreate, conn=Depends(get_db)) -> User:
    """Регистрация пользователя"""
    user = await query.get_user(data.username, conn)
    # Проверка, что пользователя не существует
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    hashed_password = bcrypt.hashpw(
        data.password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    user_id = await query.create_user(data.username, hashed_password, conn)

    return User(id=user_id, username=data.username)


@router_auth.post('/auth/login', response_model=Token)
async def login(data: UserCreate, conn=Depends(get_db)) -> Token:
    """Логин пользователя -> выдача токенов"""
    db_user = await query.get_user(data.username, conn)
    # Проверка, что такой пользователь существует и введены коректные данные
    if db_user is None or not bcrypt.checkpw(data.password.encode('utf-8'),
                                             db_user['password_hash'].encode('utf-8')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": data.username})
    refresh_token = create_access_token(data={"sub": data.username}, expires_delta=timedelta(days=1))

    redis_client.setex(f"refresh_token:{data.username}", 60 * 60 * 24 * 7, refresh_token)

    return {"access_token": access_token, "refresh_token": refresh_token}


@router_auth.post('/auth/refresh', response_model=Token)
async def refresh_token(request: TokenRefreshRequest) -> Token:
    """Обновление токена"""
    token = request.refresh_token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise auth_exception
        stored_refresh_token = redis_client.get(f"refresh_token:{username}")
        if stored_refresh_token is None:
            raise auth_exception
    except JWTError:
        raise auth_exception
    new_access_token = create_access_token(data={"sub": username})
    return {"access_token": new_access_token, "refresh_token": stored_refresh_token.decode('utf-8')}


@router_auth.post('/auth/logout')
async def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """Логаут пользователя -> удаление токена"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        redis_client.delete(f"refresh_token:{username}")
        return {"msg": "Successfully logged out"}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
