import uuid
from fastapi import Cookie, FastAPI, HTTPException, Response
from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


sample_user_123: dict[str, str] = {"username": "user123", "password": "password123"}
sample_user_456: dict[str, str] = {"username": "user456", "password": "password456"}
sample_user_789: dict[str, str] = {"username": "user789", "password": "password789"}

fake_db: list[User] = [
    User(**sample_user)
    for sample_user in [sample_user_123, sample_user_456, sample_user_789]
]

sessions: dict = {}

app = FastAPI()


@app.post("/login")
async def login(user: User, response: Response) -> dict[str, str]:
    result: User | None = next(
        (
            person
            for person in fake_db
            if person.username == user.username and person.password == user.password
        ),
        None,
    )
    if result:
        token = str(uuid.uuid4())
        sessions[token] = user
        response.set_cookie(
            key="token", value=token, httponly=True, expires=24 * 60 * 60
        )
        return {"message": "Cookie is set"}
    raise HTTPException(status_code=401, detail="Invalid username or password")


@app.get("/user")
async def user(token=Cookie(default=None)) -> dict[str, str]:
    if token:
        user: User | None = sessions.get(token)
        if user:
            return user.dict()
    raise HTTPException(status_code=401, detail="Unautorized")
