from fastapi import FastAPI, HTTPException, Request

app = FastAPI()


@app.get("/headers")
async def get_headers(request: Request):
    if all([request.headers.get("User-Agent"), request.headers.get("Accept-Language")]):
        return {
            "User-Agent": request.headers["User-Agent"],
            "Accept-Language": request.headers["Accept-Language"],
        }
    raise HTTPException(status_code=400, detail="Bad Request")
