from datetime import datetime, timedelta, UTC
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# JWT 설정
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY 환경 변수가 설정되지 않았습니다.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None 