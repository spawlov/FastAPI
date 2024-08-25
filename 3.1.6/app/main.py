from fastapi import FastAPI

app = FastAPI()

fake_items_db: list[dict[str, str]] = [
    {"item_name": "Foo"},
    {"item_name": "Bar"},
    {"item_name": "Baz"},
]


@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10) -> list[dict[str, str]]:
    return fake_items_db[skip : skip + limit]
