from contextlib import asynccontextmanager
import os
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI, HTTPException
from databases import Database
from pydantic import BaseModel
from typing import Any, Optional

load_dotenv(find_dotenv())

ASYNC_DB_URL: str = os.getenv("ASYNC_DB_URL")


class UserCreate(BaseModel):
    username: str
    email: str


class UserReturn(BaseModel):
    username: str
    email: str
    id: Optional[int] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

database = Database(ASYNC_DB_URL)


@app.post("/users/", response_model=UserReturn)
async def create_user(user: UserCreate) -> dict[str, Any]:
    query = (
        "INSERT INTO users (username, email) VALUES (:username, :email) RETURNING id"
    )
    values: dict[str, str] = {"username": user.username, "email": user.email}
    try:
        user_id = await database.execute(query=query, values=values)
        return {**user.model_dump(), "id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create user")


@app.get("/user/{user_id}", response_model=UserReturn)
async def get_user(user_id: int) -> UserReturn:
    query = "SELECT * FROM users WHERE id = :user_id"
    values: dict[str, int] = {"user_id": user_id}
    try:
        result = await database.fetch_one(query=query, values=values)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to fetch user from database"
        )
    if result:
        return UserReturn(
            username=result["username"], email=result["email"], id=result["id"]
        )
    raise HTTPException(status_code=404, detail="User not found")


@app.put("/user/{user_id}", response_model=UserReturn)
async def update_user(user_id: int, user: UserCreate) -> dict[str, Any]:
    query = "UPDATE users SET username = :username, email = :email WHERE id = :user_id"
    values: dict[str, Any] = {
        "user_id": user_id,
        "username": user.username,
        "email": user.email,
    }
    try:
        await database.execute(query=query, values=values)
        return {**user.model_dump(), "id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update user in database")


@app.delete("/user/{user_id}", response_model=dict)
async def delete_user(user_id: int) -> dict[str, str]:
    query = "DELETE FROM users WHERE id = :user_id RETURNING id"
    values: dict[str, int] = {"user_id": user_id}
    try:
        deleted_rows = await database.execute(query=query, values=values)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to delete user from database"
        )
    if deleted_rows:
        return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")
