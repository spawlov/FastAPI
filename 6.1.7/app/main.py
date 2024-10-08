from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse


app = FastAPI()


class CustomException(HTTPException):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)


@app.exception_handler(CustomException)
async def custom_exception_handler(
    request: Request, exc: CustomException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code, content={"error": exc.detail, "args": exc.args}
    )


@app.exception_handler(Exception)
async def global_exception_handler(reuest: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "args": exc.args,
        },
    )


@app.get("/items/{item_id}/")
async def read_item(item_id: int) -> dict[str, int]:
    if item_id == 42:
        raise CustomException(status_code=404, detail="Item not found")
    if item_id > 42:
        result = item_id["cghbnj"]
    return {"item_id": item_id}
