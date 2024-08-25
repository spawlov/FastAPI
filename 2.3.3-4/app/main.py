from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class User(BaseModel):
    username: str
    user_info: str


fake_db: list[dict[str, str]] = [
    {"username": "Vasya", "user_info": "любит колбасу"},
    {"username": "Katya", "user_info": "любит петь"},
]


@app.get("/users")
async def get_all_users() -> list[dict[str, str]]:
    return fake_db


@app.post("/add_user", response_model=User)
async def add_user(user: User) -> User:
    fake_db.append({"username": user.username, "user_info": user.user_info})
    return user
