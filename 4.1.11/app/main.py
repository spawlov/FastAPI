from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


USER_DATA: list[User] = []

app = FastAPI()
security = HTTPBasic()


def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)) -> User:
    user: User | None = get_user_from_db(credentials.username)
    if user and user.password == credentials.password:
        return user
    raise HTTPException(
        status_code=401,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Basic"},
    )


def get_user_from_db(username: str) -> User | None:
    return next((user for user in USER_DATA if user.username == username), None)


@app.post("/register/")
async def add_user(username: str, password: str) -> dict[str, str]:
    user = User(username=username, password=password)
    result: User | None = next(
        (user for user in USER_DATA if user.username == username), None
    )
    if result:
        raise HTTPException(status_code=401, detail=f"User {username} already exists")
    USER_DATA.append(user)
    return {"username": user.username}


@app.get("/login/")
async def login(user: User = Depends(authenticate_user)) -> dict[str, str]:
    return {"message": "You got my secret, welcome"}
