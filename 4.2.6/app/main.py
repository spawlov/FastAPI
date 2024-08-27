from datetime import datetime, timedelta
from typing import Any
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import BaseModel

SECRET_KEY = "5ac0490acfb19a6062be680316f649be0124a48ffef5422b820fb0859d9bb22a"
ALGORITHM = "HS256"
EXPIRE_TOKEN = timedelta(seconds=60 * 60)
USERS_DATA: list[dict[str, str]] = [{"username": "admin", "password": "adminpass"}]


class User(BaseModel):
    username: str
    password: str


def create_jwt_token(data: dict) -> str:
    data.update({"exp": datetime.utcnow() + EXPIRE_TOKEN})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def get_user_from_token(token: str) -> Any | None:
    try:
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    except (jwt.InvalidSignatureError, jwt.InvalidTokenError) as error:
        raise HTTPException(status_code=401, detail=str(error))
    return payload.get("sub")


def get_user(username: str) -> dict[str, str] | None:
    return next((user for user in USERS_DATA if user.get("username") == username), None)


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@app.post("/login")
async def login(user_in: User) -> dict[str, str]:
    user: dict[str, str] | None = next(
        (
            user
            for user in USERS_DATA
            if all(
                [
                    user.get("username") == user_in.username,
                    user.get("password") == user_in.password,
                ]
            )
        ),
        None,
    )
    if user:
        return {
            "access_token": create_jwt_token({"sub": user_in.username}),
            "token_type": "bearer",
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/about_me")
async def about_me(current_user: str = Depends(get_user_from_token)) -> dict[str, str]:
    user: dict[str, str] | None = get_user(current_user)
    if user:
        return user
    raise HTTPException(status_code=404, detail=f"User {current_user} not fount")
