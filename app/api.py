from typing import Annotated
from uuid import uuid4


from fastapi import Body, FastAPI, HTTPException, UploadFile
from fastapi.responses import RedirectResponse
from PIL import Image

from app.minio_client import MinioClientDep
from app.pika_queue import SendQueue


app = FastAPI()

BUCKET_NAME = "to-process"


@app.get("/")
def index():
    return {"message": "FastAPI running"}


@app.post("/upload")
async def upload_image(file: UploadFile, filename: Annotated[str | None, Body(embed=True)], minio_client: MinioClientDep):

    # TODO: give unique name to file

    if file.content_type not in ("image/png", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Must be a PNG image")

    # Verify the file is a valid PNG image
    try:
        im = Image.open(file.file)

        # verify closes image after it's finished
        im.verify()
        file.file.seek(0)  # Reset pointer for later use

    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {exc}")

    content_type = "image/png"
    filename = filename or f"{uuid4()}.png"
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
    file_url = minio_client.get_file_url(BUCKET_NAME, filename)
    if file_url:
        return RedirectResponse(file_url)

    else:
        raise HTTPException(status_code=404, detail=f"Failed to get file {filename}")