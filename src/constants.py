from fastapi.security import OAuth2PasswordBearer
import os

SCHEME = OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 10080

DB_URL = os.getenv("DATABASE_URL")

ADMIN_USERNAME = "admin"