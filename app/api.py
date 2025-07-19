from typing import Annotated
from uuid import uuid4


from fastapi import Body, FastAPI, HTTPException, UploadFile
from fastapi.responses import RedirectResponse
from PIL import Image
from tenacity import RetryError

from app.minio_client import MinioClientDep
from app.pika_queue import ReceiveQueue, SendQueue
from app.core.settings import settings


app = FastAPI()


@app.get("/")
def index():
    return {"message": "FastAPI running"}


@app.post("/upload")
async def upload_image(
    file: UploadFile,
    minio_client: MinioClientDep,
):

    # TODO: give unique name to file

    if file.content_type not in ("image/png", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Must be a PNG image")

    # Verify the file is a valid PNG image
    try:
        im = Image.open(file.file)

        # .verify() closes image after it's finished
        im.verify()
        file.file.seek(0)  # Reset pointer for later use

    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {exc}")

    content_type = "image/png"
    filename = file.filename or f"{uuid4()}.png"
    size = file.size or 0

    # TODO: Upload to minio and request queue in parallel
    try:
        minio_client.upload_file(
            settings.BUCKET_TO_PROCESS, filename, file.file, size, content_type
        )
    except RetryError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {exc}")

    # FIXME: make a new SendQueue every time?
    with SendQueue(settings.BUCKET_TO_PROCESS) as request_queue:
        request_queue.add_to_queue(filename)

    return {"message": "Image uploaded successfully"}


@app.get("/get-file")
def get_file(filename: str, minio_client: MinioClientDep):
    try:
        file_url = minio_client.get_file_url(settings.BUCKET_TO_PROCESS, filename)
    except RetryError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to get file: {exc}")

    if file_url:
        return RedirectResponse(file_url)

    else:
        raise HTTPException(status_code=404, detail=f"Failed to get file: {filename}")
