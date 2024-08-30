from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


app = FastAPI()


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc)},
    )


@app.exception_handler(RequestValidationError)
async def custom_request_validation_exception_handler(request, exc) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "message": "Custom Request Validation Error",
            "errors": str(exc.errors()),
        },
    )


@app.post("/items/")
async def create_item(item: Item) -> dict[str, Any]:
    if item.price < 0:
        raise HTTPException(status_code=400, detail="Price must be non-negative")
    return {"message": "Item created successfully", "item": item}
