from fastapi import FastAPI, HTTPException


class CustomException(HTTPException):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)


app = FastAPI()


@app.get("/items/{item_id}/")
async def read_item(item_id: int) -> dict[str, int]:
    if item_id == 42:
        raise CustomException(status_code=404, detail="Item not found")
    return {"item_id": item_id}
