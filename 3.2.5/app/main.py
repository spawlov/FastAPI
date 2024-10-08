from fastapi import Cookie, FastAPI

app = FastAPI()


@app.get("/items/")
async def read_items(ads_id: str | None = Cookie(default=None)) -> dict[str, str | None]:
    return {"ads_id": ads_id}
