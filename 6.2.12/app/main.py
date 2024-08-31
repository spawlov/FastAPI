import re
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, SecretStr

app = FastAPI()


class User(BaseModel):
    username: str
    age: int
    email: EmailStr
    password: str
    phone: Optional[str] = None


class UserResponse(BaseModel):
    id: int | None = None
    username: str
    age: int
    email: EmailStr
    password: SecretStr
    phone: Optional[str] = None


def is_valid_username(username: str) -> bool:
    pattern = r"^[a-zA-Z][a-zA-Z0-9-_\.]{1,20}$"
    return bool(re.match(pattern, username))


def is_valid_age(age: int) -> bool:
    return age >= 18 and isinstance(age, int)


def is_valid_email(email: str) -> bool:
    pattern = r"^[-\w.]+@([A-z0-9][-A-z0-9]+\.)+[A-z]{2,4}$"
    return bool(re.match(pattern, email))


def is_valid_password(password: str) -> bool:
    pattern = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&~&^#])[A-Za-z\d@$!%*?&~&^#]{8,}$"
    return bool(re.match(pattern, password))


def is_valid_phone(phone: str) -> bool:
    pattern = r"^\+?[0-9]{1,3}?[-.\s]?[0-9]{1,3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$"
    return bool(re.match(pattern, phone))


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc)},
    )


@app.exception_handler(RequestValidationError)
async def custom_request_validation_exception_handler(request, exc) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "message": "Custom Request Validation Error",
            "errors": str(exc.errors()),
        },
    )


@app.post("/signup", status_code=201, response_model=UserResponse)
async def signup(user: User) -> User:
    if not is_valid_username(user.username):
        raise HTTPException(
            status_code=400,
            detail="Username: must start with a letter, letters and numbers are allowed. From 2 to 20 characters",
        )
    if not is_valid_age(user.age):
        raise HTTPException(
            status_code=400,
            detail="Age is an integer greater than or equal to 18.",
        )
    if not is_valid_email(user.email):
        raise HTTPException(
            status_code=400,
            detail="Invalid e-mail.",
        )
    if not is_valid_password(user.password):
        raise HTTPException(
            status_code=400,
            detail="Password - characters, numbers and special characters. At least 8 characters.",
        )
    if user.phone and not is_valid_phone(user.phone):
        raise HTTPException(
            status_code=400,
            detail="Incorrect phone number.",
        )
    return user
