from uuid import uuid4

from fastapi import FastAPI, Response, UploadFile
from fastapi.responses import StreamingResponse

from app.minio_client import MinioClientDep
from app.pika_queue import SendQueue

app = FastAPI()

BUCKET_NAME = "to-process"


@app.post("/upload")
async def upload_image(file: UploadFile, minio_client: MinioClientDep):

    # TODO: check if file is a valid image
    # TODO: check empty file
    # TODO: give unique name to file

    content_type = file.content_type or "image/png"
    extension = content_type.split("/")[1]
    filename = file.filename or f"{uuid4()}.{extension}"
    size = file.size or 0

    # TODO: Upload to minio and request queue in parallel
    minio_client.upload_file(BUCKET_NAME, filename, file.file, size, content_type)

    # FIXME: make a new SendQueue every time?
    request_queue = SendQueue(BUCKET_NAME)
    request_queue.add_to_queue(filename)
    request_queue.close()

    return {"message": "Image uploaded successfully"}


@app.get("/get-file")
async def get_file(filename: str, minio_client: MinioClientDep):
    file_data, content_type = minio_client.get_file(BUCKET_NAME, filename)
    return Response(content=file_data, media_type=content_type)
