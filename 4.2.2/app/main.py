import jwt

SECRET_KEY = "711f4f1125d8f81ad30a026dbb8f2521b4558e3934c6c7e58e6822d01d027c35"
ALGORITHM = "HS256"

USERS_DATA: list[dict[str, str]] = [{"username": "admin", "password": "adminpass"}]


def create_jwt_token(data: dict) -> str:
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def get_user_from_token(token: str) -> str:
    try:
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    except jwt.InvalidSignatureError as error:
        print(error)
        return str(error)
    except jwt.InvalidTokenError as error:
        print(error)
        return str(error)
    return payload.get("sub")


def get_user(username: str) -> dict[str, str] | None:
    return next((user for user in USERS_DATA if user.get("username") == username), None)


token: str = create_jwt_token({"sub": "admin"})
print(token)

username: str = get_user_from_token(token)
print(username)

current_user: dict[str, str] | None = get_user(username)
print(current_user)
