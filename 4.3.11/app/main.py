from typing import Annotated, Any, Optional
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from pydantic import BaseModel

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

USERS_DATA: dict[str, dict[str, str]] = {
    "admin": {"username": "admin", "password": "adminpass", "role": "admin"},
    "moderator": {"username": "moderator", "password": "moderpass", "role": "moder"},
    "user": {"username": "user", "password": "userpass", "role": "user"},
}


class User(BaseModel):
    username: str
    password: str
    role: Optional[str] = None


def create_jwt_token(data: dict) -> str:
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def get_user_from_token(token: str) -> Any | None:
    try:
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    except (jwt.InvalidSignatureError, jwt.InvalidTokenError) as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload.get("sub")


def get_user(username: str) -> User | None:
    if username in USERS_DATA:
        user_data: dict[str, str] = USERS_DATA[username]
        return User(**user_data)
    return None


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/login")
def login(user_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict[str, str]:
    user_data_from_db: User | None = get_user(user_data.username)
    if user_data_from_db is None or user_data.password != user_data_from_db.password:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_jwt_token({"sub": user_data.username})}


@app.get("/post")
async def read_post(current_user: str = Depends(get_user_from_token)) -> dict[str, str]:
    user_data: User | None = get_user(current_user)
    if user_data.role not in ["admin", "moder", "user"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )
    return {"message": f"Hello, {user_data.username}!"}


@app.get("/create_post")
async def create_post(
    current_user: str = Depends(get_user_from_token),
) -> dict[str, str]:
    user_data: User | None = get_user(current_user)
    if user_data.role not in ["admin"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )
    return {"message": f"Hello, {user_data.username}!"}


@app.get("/update_post")
async def update_post(
    current_user: str = Depends(get_user_from_token),
) -> dict[str, str]:
    user_data: User | None = get_user(current_user)
    if user_data.role not in ["admin", "moder"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )
    return {"message": f"Hello, {user_data.username}!"}


@app.get("/delete_post")
async def delete_post(
    current_user: str = Depends(get_user_from_token),
) -> dict[str, str]:
    user_data: User | None = get_user(current_user)
    if user_data.role not in ["admin"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )
    return {"message": f"Hello, {user_data.username}!"}
