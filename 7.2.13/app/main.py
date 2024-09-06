from typing import Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, PositiveInt
import httpx

app = FastAPI()


class Item(BaseModel):
    id: int
    name: str


fake_db: dict = {}


@app.post("/items/", response_model=Item)
async def create_item(item: Item) -> Item:
    if item.id in fake_db:
        raise HTTPException(status_code=400, detail="Item already exists")
    fake_db[item.id] = item
    return item


@app.get("/item/{item_id}", response_model=Item)
async def read_item(item_id: int) -> Any:
    item: Any | None = fake_db.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.get("/api/places/")
async def get_places() -> Any:
    async with httpx.AsyncClient() as client:
        try:
            response: httpx.Response = await client.get(
                "https://map.s-pavlov.ru/api/places/"
            )
        except (
            httpx.TimeoutException,
            httpx.ConnectError,
        ) as error:
            raise HTTPException(status_code=408, detail=str(error))
        response.raise_for_status()
        return response.json()


@app.get("/api/place/{id}")
async def get_place(id: int) -> Any:
    if id < 0:
        raise HTTPException(status_code=400, detail="Id mast be positive or 0")
    async with httpx.AsyncClient() as client:
        try:
            response: httpx.Response = await client.get(
                "https://map.s-pavlov.ru/api/places/"
            )
        except (
        httpx.TimeoutException,
        httpx.ConnectError,
        ) as error:
            raise HTTPException(status_code=408, detail=str(error))
        response.raise_for_status()
        try:
            result: dict = response.json()[id]
        except IndexError:
            raise HTTPException(status_code=404, detail="Item not found")
        return result
