import os
import importlib
from unittest.mock import patch
from fastapi.testclient import TestClient

fake_env = {
        "SPARQL_ENDPOINT": "https://fake.example.org/sparql",
        "CONFIG_YML": "/config/default.yml",
        "SPARQL_TIMEOUT": "30",
        "SPARQL_REQUEST_METHOD": "GET"
    }

class FakeApi:
    def __init__(self, *args, **kwargs):
        pass
    def getManifest(self, *, type, id):
        if type == "nonexistent_type":
            raise Exception("not found")
        return {"ok": True, "id": f"{type}/{id}"}

with patch.dict(os.environ, fake_env, clear=False):
    import lib.Api as api_mod
    with patch.object(api_mod, "Api", FakeApi):
        import main
        importlib.reload(main)  # ensure patched env/Api are used
        app = main.app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "<h1>SARI IIIF Manifest Service</h1>" in response.text

def test_get_manifest_not_found():
    response = client.get("/manifest/nonexistent_type/nonexistent_id")
    assert response.status_code == 500