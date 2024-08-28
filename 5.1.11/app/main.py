import os
from typing import Annotated, Any, List, Optional, Tuple
from dotenv import find_dotenv, load_dotenv
from fastapi import Body, FastAPI, HTTPException, Path
from pydantic import BaseModel
from sqlalchemy import Delete, Select, delete, insert, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column,
    sessionmaker,
)
from sqlalchemy.sql.dml import ReturningInsert

load_dotenv(find_dotenv())

ASYNC_DB_URL: str = os.getenv("ASYNC_DB_URL")

engine: AsyncEngine = create_async_engine(ASYNC_DB_URL, echo=True)
Base: Any = declarative_base()
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Todo(Base):
    __tablename__: str = "todo_list"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    completed: Mapped[bool] = mapped_column(nullable=False, default=False)


class CreateTodo(BaseModel):
    title: str = None
    description: Optional[str] = None
    completed: Optional[bool] = False


class ReturnTodo(BaseModel):
    id: int
    title: str
    description: str
    completed: bool


class UpdateTodo(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


app = FastAPI()


@app.post("/create_todo")
async def create_todo(todo: CreateTodo = Body()) -> ReturnTodo:
    async with async_session() as session:
        query: ReturningInsert[Tuple[int, str, str, bool]] = (
            insert(Todo)
            .values(**todo.model_dump())
            .returning(Todo.id, Todo.title, Todo.description, Todo.completed)
        )
        query_result = await session.execute(query)
        todo_result = query_result.mappings().one()
        await session.commit()
        return ReturnTodo(**todo_result)


@app.get("/")
async def get_todos(limit: Optional[int] = 10) -> List[ReturnTodo]:
    async with async_session() as session:
        query: Select[Tuple[int, str, str, bool]] = select(
            Todo.__table__.columns
        ).limit(limit).order_by("id")
        query_result = await session.execute(query)
        todo_result = query_result.mappings().all()
        if todo_result:
            return todo_result
        raise HTTPException(status_code=404, detail="Item(s) not found")


@app.get("/{id_todo}")
async def get_todo_by_id(id_todo: Annotated[int, Path()]) -> ReturnTodo:
    async with async_session() as session:
        query: Select[Tuple[int, str, str, bool]] = select(
            Todo.__table__.columns
        ).where(Todo.id == id_todo)
        query_result = await session.execute(query)
        todo_result = query_result.mappings().one_or_none()
        if todo_result:
            return todo_result
        raise HTTPException(status_code=404, detail="Item not found")


@app.put("/update_todo/{id_todo}")
async def update_todo(
    id_todo: Annotated[int, Path()], todo: UpdateTodo = Body()
) -> ReturnTodo:
    async with async_session() as session:
        existing_todo = await session.get(Todo, id_todo)
        if existing_todo is None:
            raise HTTPException(status_code=404, detail="Item not found")

        if todo.title:
            existing_todo.title = todo.title
        if todo.description:
            existing_todo.description = todo.description
        if todo.completed:
            existing_todo.completed = todo.completed

        session.add(existing_todo)
        await session.commit()
        return existing_todo


@app.delete("/delete/{id_todo}")
async def delete_todo(id_todo: Annotated[int, Path()]) -> dict[str, str]:
    async with async_session() as session:
        query: Delete = delete(Todo).where(Todo.id == id_todo)
        query_result = await session.execute(query)
        result = query_result.rowcount
        if result:
            await session.commit()
            return {"message": f"Item id={id_todo} is deleted"}
        raise HTTPException(status_code=404, detail="Item not found")
