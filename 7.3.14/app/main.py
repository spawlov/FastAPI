import os
from typing import Any, Tuple
from dotenv import find_dotenv, load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, PositiveInt
from sqlalchemy import (
    Column,
    Engine,
    Integer,
    Result,
    RowMapping,
    Select,
    String,
    create_engine,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.sql.dml import ReturningInsert

load_dotenv(find_dotenv())

Base = declarative_base()
Engine = create_engine(os.getenv("APP_DB_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)


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


app = FastAPI()


Base.metadata.create_all(bind=Engine)


def get_db():
    Session = SessionLocal()
    try:
        yield Session
    finally:
        Session.close()


@app.post("/create_user/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    name_exists_query: Select[Tuple[User]] = select(User).where(User.name == user.name)
    name_exists_result: Result[Tuple[User]] = db.execute(name_exists_query)
    if name_exists_result.scalar():
        raise HTTPException(status_code=400, detail="User already registered")

    email_exists_query: Select[Tuple[User]] = select(User).where(
        User.email == user.email
    )
    email_exists_result: Result[Tuple[User]] = db.execute(email_exists_query)
    if email_exists_result.scalar():
        raise HTTPException(status_code=400, detail="Email already registered")

    query: ReturningInsert[Tuple[int, str, str]] = (
        insert(User)
        .values(**user.model_dump())
        .returning(User.id, User.name, User.email)
    )
    query_result: Result[Tuple[int, str, str]] = db.execute(query)
    user_result: RowMapping = query_result.mappings().one()
    db.commit()

    return UserResponse(**user_result)


@app.get("/user/{user_id}", response_model=UserResponse, status_code=200)
def get_user_by_id(user_id: PositiveInt, db: Session = Depends(get_db)) -> UserResponse:
    query: Select[Tuple[User]] = select(User).where(User.id == user_id)
    result: User | None = db.execute(query).scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    user: dict[str, Any] = {"id": result.id, "name": result.name, "email": result.email}
    return UserResponse(**user)


@app.put("/update_user/{user_id}", response_model=UserResponse, status_code=200)
def update_user(
    user_id: PositiveInt, user: UserCreate, db: Session = Depends(get_db)
) -> UserResponse:
    query: Select[Tuple[User]] = select(User).where(User.id == user_id)
    result: User | None = db.execute(query).scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    query = (
        update(User)
        .where(User.id == user_id)
        .values(**user.model_dump())
        .returning(User.id, User.name, User.email)
    )

    query_result: Result[Tuple[int, str, str]] = db.execute(query)
    user_result: RowMapping = query_result.mappings().one()
    db.commit()

    return UserResponse(**user_result)


@app.delete("/delete_user/{user_id}", status_code=200)
def delete_user(user_id: PositiveInt, db: Session = Depends(get_db)) -> JSONResponse:
    query: Select[Tuple[User]] = select(User).where(User.id == user_id)
    result: User | None = db.execute(query).scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    query = delete(User).where(User.id == user_id)
    db.execute(query)
    db.commit()

    return JSONResponse(
        status_code=200, content={"detail": f"User id={user_id} deleted"}
    )
