from uuid import uuid4

from fastapi.testclient import TestClient
import httpx

from app.api import app
from .generate_random_image import generate_random_image

client = TestClient(app)

filename = f"dog.png"


def test_api():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "FastAPI running"}


def test_upload_image():
    file = generate_random_image(filename)
    response = client.post("/upload", files={"file": file})
    assert response.status_code == 200
    assert response.json() == {"message": "Image uploaded successfully"}


def test_get_file():
    response = client.get(
        "/get-file", params={"filename": filename}, follow_redirects=False
    )
    assert response.status_code == 307
    assert "minio" in response.headers["Location"].lower()

    response = httpx.get(response.headers["Location"])
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/png"
