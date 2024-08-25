from typing import Annotated, Optional
from pydantic import BaseModel, Field, SecretStr


class User(BaseModel):
    username: str
    password: str
    token: Annotated[str, Field(default=None, exclude=False)]
