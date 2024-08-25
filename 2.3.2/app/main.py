from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/{user_id}")
async def search_user_by_id(user_id: int) -> dict[str, int]:
    if user_id < 0:
        raise HTTPException(status_code=400, detail="Bad Request")
    return {"Вы просили найти юзера с id": user_id}
