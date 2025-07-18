from uuid import uuid4

from fastapi.testclient import TestClient

from app.api import app
from .generate_random_image import generate_random_image

client = TestClient(app)

filename = f"{uuid4()}.png"


def test_api():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "FastAPI running"}


def test_upload_image():
    response = client.post("/upload", files={"file": generate_random_image()})
    assert response.status_code == 200
    assert response.json() == {"message": "Image uploaded successfully"}


def test_get_file():
    response = client.get("/get-file", params={"filename": filename})
    assert response.status_code == 307
    assert "minio" in response.headers["Location"].lower()

    response = client.get(response.headers["Location"])
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/png"
