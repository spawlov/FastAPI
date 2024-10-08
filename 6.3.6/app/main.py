from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse

app = FastAPI()


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc) -> PlainTextResponse:
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc) -> PlainTextResponse:
    return PlainTextResponse(str(exc), status_code=400)


@app.get("/items/{item_id}")
async def read_item(item_id: int) -> dict[str, int]:
    if item_id == 3:
        raise HTTPException(status_code=418, detail="Nope! I don't like 3.")
    return {"item_id": item_id}
