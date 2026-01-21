from fastapi.testclient import TestClient
from src.forestfires_project.api import app
import os
import random

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "YOLO Inference API" in response.json()["message"]


def test_device_endpoint():
    response = client.get("/device")
    assert response.status_code == 200
    assert "cuda" in response.json()["device"] or "cpu" in response.json()["device"]


def test_predict_endpoint():
    # Get a random image from the folder
    folder_path = "data/processed/test/images"
    image_files = [f for f in os.listdir(folder_path) if f.endswith((".jpg", ".jpeg", ".png"))]
    assert image_files, "No image files found in the folder"

    random_image = random.choice(image_files)
    image_path = os.path.join(folder_path, random_image)

    with open(image_path, "rb") as image:
        files = {"file": image}
        response = client.post("/predict", files=files)
    assert response.status_code == 200
    assert "detections" in response.json()
