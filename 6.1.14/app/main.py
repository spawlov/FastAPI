from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()


class CustomExcetpionResponse(BaseModel):
    code: int
    error: str


class GlobalExceptionResponse(BaseModel):
    code: int
    error: str
    args: list | None = None


class CustomException(HTTPException):
    def __init__(
        self,
        detail: str,
        status_code: int = 400,
    ):
        super().__init__(status_code=status_code, detail=detail)


@app.exception_handler(CustomException)
async def custom_exception_handler(
    request: Request,
    exc: CustomExcetpionResponse,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    reuest: Request, exc: GlobalExceptionResponse
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "error": "Internal server error",
            "args": exc.args,
        },
    )


@app.get("/raise_custom_exception")
async def raise_custom_exception(value: int) -> JSONResponse:
    if value < 0:
        raise CustomException(
            status_code=409, detail={"code": 409, "error": "Invalid value"}
        )
    if value == 0:
        raise CustomException(
            status_code=400, detail={"code": 400, "error": "Bad request"}
        )

    if 0 < value < 10:
        raise CustomException(
            status_code=404, detail={"code": 404, "error": "Not found"}
        )

    return JSONResponse({"code": 200, "item_id": value})


@app.get("/raise_global_extension")
async def raise_global_extension():
    a = 1 / 0
