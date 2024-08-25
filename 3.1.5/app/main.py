from typing import Annotated

from fastapi import FastAPI, File, UploadFile

app = FastAPI()


@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]) -> dict[str, int]:
    return {"filesize": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(uploaded_file: UploadFile):
    payload: bytes = await uploaded_file.read()
    with open(uploaded_file.filename, "wb") as file:
        file.write(payload)
    return {"filename": uploaded_file.filename, "filesize": uploaded_file.size}
