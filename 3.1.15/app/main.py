from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field, PositiveInt


class UserCreate(BaseModel):
    name: str = Field(..., description="Имя пользователя (обязательно)")
    email: EmailStr = Field(
        ...,
        description="Адрес электронной почты пользователя (обязателен и должен иметь допустимый формат)",
    )
    age: PositiveInt = Field(
        None,
        description="Возраст пользователя (необязательно, но должно быть положительным целым числом, если указано)",
    )
    is_subscribed: bool = Field(
        False,
        description="Флажок, указывающий, подписан ли пользователь на новостную рассылку (необязательно)",
    )


app = FastAPI()


@app.post("/create_user/", response_model=UserCreate)
async def create_user(user: UserCreate) -> UserCreate:
    return user
