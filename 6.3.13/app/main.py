from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, SecretStr
from typing import Any
import time

app = FastAPI()


class User(BaseModel):
    username: str
    email: EmailStr
    password: SecretStr


class ErrorResponseModel(BaseModel):
    status_code: int
    message: str
    error_code: str


class UserNotFoundException(Exception):
    def __init__(self, username: str) -> None:
        self.username: str = username


class InvalidUserDataException(Exception):
    def __init__(self, message: str) -> None:
        self.message: str = message


users_db: dict = {}


@app.post("/register", response_model=User)
async def register_user(user: User) -> User:
    if user.username in users_db:
        raise InvalidUserDataException("User already exists.")

    users_db[user.username] = user
    return user


@app.get("/users/{username}", response_model=User)
async def get_user(username: str) -> Any:
    if username not in users_db:
        raise UserNotFoundException(username)

    return users_db[username]



@app.exception_handler(UserNotFoundException)
async def user_not_found_exception_handler(request, exc: UserNotFoundException) -> JSONResponse:
    start_time: float = time.time()
    response = ErrorResponseModel(
        status_code=404,
        message=f"User '{exc.username}' not found.",
        error_code="user_not_found",
    )
    response_time: float = time.time() - start_time
    return JSONResponse(
        content=response.model_dump(), headers={"X-ErrorHandleTime": str(response_time)}
    )


@app.exception_handler(InvalidUserDataException)
async def invalid_user_data_exception_handler(request, exc: InvalidUserDataException) -> JSONResponse:
    start_time: float = time.time()
    response = ErrorResponseModel(
        status_code=400, message=exc.message, error_code="invalid_user_data"
    )
    response_time: float = time.time() - start_time
    return JSONResponse(
        content=response.model_dump(), headers={"X-ErrorHandleTime": str(response_time)}
    )
