import os
from dotenv import find_dotenv, load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Any, Tuple
from pydantic.types import PositiveInt
from sqlalchemy import (
    Result,
    RowMapping,
    Select,
    Column,
    Integer,
    insert,
    select,
    String,
)
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.dml import ReturningInsert

load_dotenv(find_dotenv())

app = FastAPI()

Engine = create_async_engine(os.getenv("APP_DB_URL"), echo=True)
SessionLocal = async_sessionmaker(Engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    email = Column(String, unique=True)


class UserCreate(BaseModel):
    name: str
    email: EmailStr


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr


@app.on_event("startup")
async def startup():
    async with Engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_db(testing: bool = False):
    Session = SessionLocal()
    try:
        yield Session
    finally:
        Session.close()


@app.post("/create_user/", response_model=UserResponse)
async def create_user(
    user: UserCreate, db: AsyncSession = Depends(get_db)
) -> UserResponse:

    name_exists_query: Select[Tuple[User]] = select(User).where(User.name == user.name)
    name_exists_result: Result[Tuple[User]] = await db.execute(name_exists_query)
    if name_exists_result.scalar():
        raise HTTPException(status_code=400, detail="User already registered")

    email_exists_query: Select[Tuple[User]] = select(User).where(
        User.email == user.email
    )
    email_exists_result: Result[Tuple[User]] = await db.execute(email_exists_query)
    if email_exists_result.scalar():
        raise HTTPException(status_code=400, detail="Email already registered")

    query: ReturningInsert[Tuple[int, str, str]] = (
        insert(User)
        .values(**user.model_dump())
        .returning(User.id, User.name, User.email)
    )
    query_result: Result[Tuple[int, str, str]] = await db.execute(query)
    user_result: RowMapping = query_result.mappings().one()
    await db.commit()

    return UserResponse(**user_result)


# @app.get("/user/{user_id}")  # , response_model=User)
# def get_user(user_id: PositiveInt):
#     db = SessionLocal()
#     user = db.query(User).filter(User.id == user_id).one()
#     if user:
#         return user
#     raise HTTPException(status_code=404, detail="User not found")


# @app.put("/user/{user_id}")  # , response_model=User)
# def update_user(user_id: PositiveInt, user: UserUpdate):
#     db = SessionLocal()
#     db_user = db.query(User).filter(User.id == user_id).first()
#     if user.name:
#         db_user.name = user.name
#     if user.email:
#         db_user.email = user.email
#     db.commit()
#     db.refresh(db_user)
#     return db_user
