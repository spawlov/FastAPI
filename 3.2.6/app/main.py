from datetime import datetime, timedelta
import re
from typing import Any
from fastapi import Cookie, FastAPI, Response

app = FastAPI()


@app.get("/")
def root(response: Response, last_visit=Cookie(default=None)) -> dict[str, Any]:
    now: str = datetime.now().strftime("%d.%m.%Y, %H:%M:%S")
    if last_visit:
        return {"last_visit": last_visit}
    response.set_cookie(key="last_visit", value=now, expires=60 * 60)
    return {"message": "Cookies is set"}
