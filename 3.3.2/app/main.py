from typing import Annotated
from fastapi import FastAPI, Header

app = FastAPI()


@app.get("/items/")
async def read_items(
    user_agent: Annotated[str | None, Header()] = None
) -> dict[str, str | None]:
    return {"User Agent": user_agent}
