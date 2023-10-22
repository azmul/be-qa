
from __future__ import annotations
from datetime import datetime, timedelta
from jose import JWTError, jwt
from schemas import TokenData

# openssl rand -hex 32
SECRET_KEY = "016438d2713516b6ed02ae6017ed2e00ac73e370f06c61e1b1dd289e081ba25e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1000

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception