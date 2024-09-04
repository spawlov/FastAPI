from fastapi import FastAPI

app = FastAPI()


@app.get("/sum")
async def get_sum(a: int, b: int) -> dict[str, int]:
    return {"result": a + b}
