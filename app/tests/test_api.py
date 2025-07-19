from io import BytesIO
from uuid import uuid4

from PIL import Image, ImageChops
from fastapi.testclient import TestClient
import httpx

from app.api import app
from .generate_random_image import generate_random_image

client = TestClient(app)


def make_filename():
    return f"{uuid4()}.png"


# from:
# https://stackoverflow.com/questions/23660929/how-to-check-whether-a-jpeg-image-is-color-or-gray-scale-using-only-python-stdli
def is_grayscale(im: Image.Image) -> bool:
    if im.mode in ("1", "L", "LA"):
        return True

    converted = im.convert("L").convert(im.mode)
    diff = ImageChops.difference(im, converted)

    return diff.getbbox() is None


def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "FastAPI running"}


def test_upload_image():
    file = generate_random_image(make_filename())
    response = client.post("/upload", files={"file": file})
    assert response.status_code == 200
    assert response.json() == {"message": "Image uploaded successfully"}


def test_get_uploaded_file():
    filename = make_filename()
    file = generate_random_image(filename)
    response = client.post("/upload", files={"file": file})

    response = client.get(
        "/get-uploaded-file", params={"filename": filename}, follow_redirects=False
    )
    assert response.status_code == 307
    assert "minio" in response.headers["Location"].lower()

    response = httpx.get(response.headers["Location"])
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/png"


def test_get_processed_file():
    filename = make_filename()
    file = generate_random_image(filename)
    response = client.post("/upload", files={"file": file})

    response = client.get(
        "/get-processed-file", params={"filename": filename}, follow_redirects=False
    )
    assert response.status_code == 307
    assert "minio" in response.headers["Location"].lower()

    response = httpx.get(response.headers["Location"])
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/png"

    # check if image is grayscale
    image = Image.open(BytesIO(response.content))
    assert is_grayscale(image)


def test_upload_pdf():
    with open("./app/tests/data/cpumemory.pdf", "rb") as f:
        response = client.post("/upload", files={"file": f})
    assert response.status_code == 400
