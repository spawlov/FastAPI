from typing import Any
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


USER_DATA: list[User] = [
    User(**{"username": "user1", "password": "pass1"}),
    User(**{"username": "user2", "password": "pass2"}),
]

app = FastAPI()
security = HTTPBasic()


def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)) -> User:
    user: User | None = get_user_from_db(credentials.username)
    if user and user.password == credentials.password:
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
    )


def get_user_from_db(username: str) -> User | None:
    return next((user for user in USER_DATA if user.username == username), None)


@app.get("/protected_resource/")
def get_protected_resource(user: User = Depends(authenticate_user)) -> dict[str, Any]:
    return {"message": "You have access to the protected resource!", "user_info": user}
