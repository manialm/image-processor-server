from uuid import uuid4

from fastapi import FastAPI, UploadFile

from app.minio_client import MinioClient

app = FastAPI()


@app.post("/upload")
async def upload_image(file: UploadFile):
    minio_client = MinioClient()

    # TODO: check if file is a valid image
    # TODO: check empty file
    # TODO: give unique name to file

    content_type = file.content_type or "image/png"
    extension = content_type.split("/")[1]
    filename = file.filename or f"{uuid4()}.{extension}"
    size = file.size or 0

    minio_client.upload_file("to-process", filename, file.file, size, content_type)

    return {"message": "Image uploaded successfully"}
