import os
from datetime import datetime, timedelta
import re
from dotenv import load_dotenv, find_dotenv
from typing import Annotated, Any
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import BaseModel, Field, SecretStr, StringConstraints
from cryptography.fernet import Fernet

load_dotenv(find_dotenv())


class User(BaseModel):
    username: Annotated[
        str,
        StringConstraints(min_length=2, max_length=20),
        Field(description="Имя пользователя (2..20 латинских символов + цифры)"),
    ]
    password: Annotated[
        SecretStr,
        StringConstraints(min_length=8),
        Field(description="Пароль (8..20 латинских символов + цифры)"),
    ]


EXPIRE_TOKEN = timedelta(seconds=int(os.getenv("EXPIRE_TIME", 60)))


def get_fernet_key() -> bytes:
    key: str | None = os.getenv("FERNET_KEY")
    if not key:
        key = Fernet.generate_key()
        os.environ["FERNET_KEY"] = key.decode()
    else:
        key = key.encode()
    return key


fernet = Fernet(get_fernet_key())


def create_jwt_token(data: dict) -> str:
    data.update({"exp": datetime.utcnow() + EXPIRE_TOKEN})
    return jwt.encode(
        data,
        os.getenv("SECRET_KEY", "FakeKey"),
        algorithm=os.getenv("ALGORITHM", "HS256"),
    )


def get_user_from_token(token: str) -> Any | None:
    try:
        payload: dict = jwt.decode(
            token, os.getenv("SECRET_KEY"), algorithms=os.getenv("ALGORITHM")
        )
    except (jwt.InvalidSignatureError, jwt.InvalidTokenError) as error:
        raise HTTPException(status_code=401, detail=str(error))
    return payload.get("sub")


def is_username_valid(username: str) -> bool:
    if not (2 <= len(username) <= 20):
        return False
    if not re.match(r"^[a-zA-Z0-9]+$", username):
        return False
    return True


def is_password_valid(password: str) -> bool:
    if not (8 <= len(password) <= 20):
        return False
    if not re.search(r"[a-zA-Z]", password) or not re.search(r"[0-9]", password):
        return False
    return True


fake_db: list[User] = []


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@app.post("/register")
async def add_user(username: str, password: str) -> User:
    if not is_username_valid(username):
        raise HTTPException(status_code=400, detail="Invalid username")

    if not is_password_valid(password):
        raise HTTPException(status_code=400, detail="Invalid password")

    result: User | None = next(
        (user for user in fake_db if user.username == username), None
    )
    if result:
        raise HTTPException(status_code=401, detail=f"User {username} already exists")

    encrypted_password: str = fernet.encrypt(password.encode("utf-8")).decode("utf-8")
    user = User(username=username, password=SecretStr(encrypted_password))
    fake_db.append(user)
    return user


@app.post("/login")
async def login(user_in: User) -> dict[str, str]:
    user: User | None = next(
        (user for user in fake_db if user.username == user_in.username), None
    )
    if user:
        decrypted_password: str = fernet.decrypt(
            user.password.get_secret_value().encode("utf-8")
        ).decode("utf-8")
        if decrypted_password == user_in.password.get_secret_value():
            return {"access_token": create_jwt_token({"sub": user_in.username})}
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/protected_resource")
async def procected_resource(token: str = Depends(oauth2_scheme)) -> dict[str, str]:
    try:
        payload: dict = jwt.decode(
            token, os.getenv("SECRET_KEY"), algorithms=os.getenv("ALGORITHM")
        )
    except (jwt.InvalidSignatureError, jwt.InvalidTokenError) as error:
        raise HTTPException(
            status_code=401, detail=str(error), headers={"WWW-Authenticate": "Bearer"}
        )
    return {"message": f"Access granted! Welcome {payload['sub']}!"}
