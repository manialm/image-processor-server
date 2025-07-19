from typing import Annotated
from uuid import uuid4


from fastapi import Body, FastAPI, HTTPException, UploadFile
from fastapi.responses import RedirectResponse
from PIL import Image
from tenacity import RetryError

from app.db import DB
from app.minio_client import MinioClientDep
from app.pika_queue import ReceiveQueue, SendQueue
from app.core.settings import settings


app = FastAPI()


@app.get("/")
def index():
    return {"message": "FastAPI running"}


def verify_content_type(file: UploadFile):
    if file.content_type not in ("image/png", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Must be a PNG image")


def verify_image_is_valid(file: UploadFile):
    try:
        im = Image.open(file.file)

        # .verify() closes image after it's finished
        im.verify()
        file.file.seek(0)

    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {exc}")


def upload_image_to_minio(
    filename: str, file: UploadFile, minio_client: MinioClientDep
):

    content_type = "image/png"
    size = file.size or 0

    try:
        minio_client.upload_file(
            settings.BUCKET_TO_PROCESS, filename, file.file, size, content_type
        )
    except RetryError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {exc}")


@app.post("/upload")
def upload_image(
    file: UploadFile,
    minio_client: MinioClientDep,
):
    try:
        return try_upload_image(file, minio_client)
    except HTTPException:
        with SendQueue(settings.BUCKET_PROCESSED) as queue:
            queue.add_to_queue(f"Failed to process {file.filename}")
        raise


def try_upload_image(
    file: UploadFile,
    minio_client: MinioClientDep,
):

    # TODO: give unique name to file
    verify_content_type(file)
    verify_image_is_valid(file)

    filename = file.filename or f"{uuid4()}.png"

    upload_image_to_minio(filename, file, minio_client)

    # FIXME: make a new SendQueue every time?
    with SendQueue(settings.BUCKET_TO_PROCESS) as request_queue:
        request_queue.add_to_queue(filename)

    return {"message": "Image uploaded successfully"}


def get_file(filename: str, bucket: str, minio_client: MinioClientDep):
    try:
        file_url = minio_client.get_file_url(settings.BUCKET_TO_PROCESS, filename)
    except RetryError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to get file: {exc}")

    if file_url:
        return RedirectResponse(file_url)

    else:
        raise HTTPException(status_code=404, detail=f"Failed to get file: {filename}")


@app.get("/get-uploaded-file")
def get_uploaded_file(filename: str, minio_client: MinioClientDep):
    return get_file(filename, settings.BUCKET_TO_PROCESS, minio_client)


@app.get("/get-processed-file")
def get_processed_file(filename: str, minio_client: MinioClientDep):
    return get_file(filename, settings.BUCKET_PROCESSED, minio_client)


@app.get("/processed")
def processed():
    with DB() as db:
        messages = db.get_messages()

    return {"messages": messages}
