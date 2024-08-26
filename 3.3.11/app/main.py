import re
from fastapi import FastAPI, HTTPException, Request

app = FastAPI()


@app.get("/headers")
async def headers(request: Request) -> dict[str, str]:
    pattern = r"^(\*|[a-z]{2}(-[A-Z]{2})*)(,\s*[a-z]{2}(-[A-Z]{2})*;q=0\.\d)*"
    if all(
        [
            request.headers.get("user-agent"),
            request.headers.get("accept-language"),
            re.match(pattern, request.headers.get("accept-language")),
        ]
    ):
        return {
            "User-Agent": request.headers["user-agent"],
            "Accept-Language": request.headers["accept-language"],
        }
    raise HTTPException(400, "Bad Request")
