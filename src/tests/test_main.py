from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "<h1>SARI IIIF Manifest Service</h1>" in response.text

def test_get_manifest_not_found():
    response = client.get("/manifest/nonexistent_type/nonexistent_id")
    assert response.status_code == 500