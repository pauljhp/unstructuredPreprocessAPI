from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import List
import os
from models import User

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("HASH_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the JWT token and extract the username
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return User(username=username, password=None)
