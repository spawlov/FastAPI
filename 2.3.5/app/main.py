from fastapi import FastAPI, HTTPException

app = FastAPI()

fake_users: dict[int, dict[str, str]] = {
    1: {"username": "john_doe", "email": "john@example.com"},
    2: {"username": "jane_smith", "email": "jane@example.com"},
}


@app.get("/users/{user_id}")
async def read_user(user_id: int) -> dict[str, str]:
    if user_id in fake_users:
        return fake_users.get(user_id)
    raise HTTPException(status_code=404, detail=f"{user_id = } not found")
