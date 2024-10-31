import os

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30

SECRET_KEY = '81dad6bf370116f9524939ff4daab3dae996797165af752bbdf7f7d4b3143a91'

USER = os.getenv('NAME_USER')
DATABASE = os.getenv('DB')
PASSWORD = os.getenv('PASS_WEB')


app = FastAPI()
