import os
import time
import socket
import importlib
from threading import Thread

import pytest
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient


def make_stub_app() -> FastAPI:
    app = FastAPI()

    @app.api_route("/sparql", methods=["GET", "POST"])
    async def sparql(request: Request):
        query = request.query_params.get("query")
        if not query:
            body = (await request.body()).decode("utf-8", errors="ignore")
            # very lenient: look for "query=" then decode-ish
            if "query=" in body:
                query = body.split("query=", 1)[1]
                # undo a couple common encodings just enough for our simple matching
                query = query.replace("%0A", "\n").replace("%20", " ").replace("+", " ")

        q = (query or "").lower()
        if "nonexistent_id" in q:
            return JSONResponse({"head": {"vars": []}, "results": {"bindings": []}},
                                media_type="application/sparql-results+json")

        if "select ?s ?p ?o" in q and "limit 1" in q:
            return JSONResponse({"head": {"vars": ["s", "p", "o"]}, "results": {"bindings": []}},
                                media_type="application/sparql-results+json")

        if "select ?label where" in q:
            return JSONResponse({
                "head": {"vars": ["label"]},
                "results": {"bindings": [{"label": {"type": "literal", "value": "Sample Label"}}]}
            }, media_type="application/sparql-results+json")

        if "select ?label ?value where" in q:
            return JSONResponse({
                "head": {"vars": ["label", "value"]},
                "results": {"bindings": [{
                    "label": {"type": "literal", "value": "Sample Label"},
                    "value": {"type": "uri", "value": "http://example.org/value"}
                }]}
            }, media_type="application/sparql-results+json")

        if "select ?image ?width ?height where" in q:
            return JSONResponse({
                "head": {"vars": ["image", "width", "height"]},
                "results": {"bindings": [{
                    "image": {"type": "uri", "value": "https://iiif.example/img.jpg"},
                    "width": {"type": "literal", "value": "1000"},
                    "height": {"type": "literal", "value": "800"},
                }]}
            }, media_type="application/sparql-results+json")

        if "select ?thumbnail ?width ?height where" in q:
            return JSONResponse({
                "head": {"vars": ["thumbnail", "width", "height"]},
                "results": {"bindings": [{
                    "thumbnail": {"type": "uri", "value": "https://iiif.example/thumb.jpg"},
                    "width": {"type": "literal", "value": "200"},
                    "height": {"type": "literal", "value": "160"},
                }]}
            }, media_type="application/sparql-results+json")

        if "select ?type where" in q:
            return JSONResponse({
                "head": {"vars": ["type"]},
                "results": {"bindings": [{"type": {"type": "uri", "value": "http://example.org/type"}}]}
            }, media_type="application/sparql-results+json")

        if "select ?value" in q:
            return JSONResponse({
                "head": {"vars": ["value"]},
                "results": {"bindings": [{"value": {"type": "uri", "value": "https://example.org/value"}}]}
            }, media_type="application/sparql-results+json")

        # default: empty result set
        return JSONResponse({"head": {"vars": []}, "results": {"bindings": []}},
                            media_type="application/sparql-results+json")

    return app


def wait_port(host: str, port: int, timeout: float = 5.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=0.3):
                return True
        except OSError:
            time.sleep(0.05)
    return False


@pytest.fixture(scope="session")
def sparql_stub():
    host, port = "127.0.0.1", 18080
    app = make_stub_app()
    config = uvicorn.Config(app, host=host, port=port, log_level="error")
    server = uvicorn.Server(config)
    t = Thread(target=server.run, daemon=True)
    t.start()
    assert wait_port(host, port, timeout=5), "SPARQL stub failed to start"
    try:
        yield f"http://{host}:{port}/sparql"
    finally:
        server.should_exit = True
        t.join(timeout=5)


@pytest.fixture
def client(monkeypatch, sparql_stub, tmp_path):
    monkeypatch.setenv("SPARQL_ENDPOINT", sparql_stub)

    cfg = "/config/default.yml"

    monkeypatch.setenv("CONFIG_YML", str(cfg))
    monkeypatch.setenv("SPARQL_TIMEOUT", "30")
    monkeypatch.setenv("SPARQL_REQUEST_METHOD", "GET")

    import sys
    if "main" in sys.modules:
        importlib.reload(sys.modules["main"])
        main = sys.modules["main"]
    else:
        import main  # noqa: F401
        main = importlib.import_module("main")

    return TestClient(main.app)


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "<h1>SARI IIIF Manifest Service</h1>" in r.text


def test_manifest_happy_path(client):
    r = client.get("/manifest/object/123")
    assert r.status_code == 200
    data = r.json()
    assert data["@context"] == "http://iiif.io/api/presentation/3/context.json"
    assert data["type"] == "Manifest"
    assert data["id"] == "http://iiif.example.com/manifest/object/123"
    assert data["label"] == {'none': ["Sample Label"]}
    assert "metadata" in data
    assert isinstance(data["metadata"], list)
    assert len(data["metadata"]) == 1
    assert data["metadata"][0]["label"] == {'none': ['Label']}
    assert data["metadata"][0]["value"] == {'none': ['https://example.org/value']}
    assert "requiredStatement" in data
    assert data["requiredStatement"]["label"] == {'none': ['Sample Label']}
    assert data["requiredStatement"]["value"] == {'none': ['http://example.org/value']}
    assert data["rights"] == "https://example.org/value"
    assert "thumbnail" in data
    assert isinstance(data["thumbnail"], list)
    assert len(data["thumbnail"]) == 1
    thumb = data["thumbnail"][0]
    assert thumb["id"] == "https://iiif.example/thumb.jpg/full/max/0/default.jpg"
    assert thumb["type"] == "Image"
    assert thumb["height"] == 160
    assert thumb["width"] == 200
    assert "service" in thumb
    assert isinstance(thumb["service"], list)
    assert len(thumb["service"]) == 1
    thumb_svc = thumb["service"][0]
    assert thumb_svc["id"] == "https://iiif.example/thumb.jpg"
    assert thumb_svc["type"] == "ImageService3"
    assert thumb_svc["profile"] == "level1"
    assert thumb["format"] == "image/jpeg"
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) == 1
    canvas = data["items"][0]
    assert canvas["id"] == "http://iiif.example.com/manifest/object/123/image/0/canvas"
    assert canvas["type"] == "Canvas"
    assert canvas["height"] == 800
    assert canvas["width"] == 1000
    assert "items" in canvas
    assert isinstance(canvas["items"], list)
    assert len(canvas["items"]) == 1
    ann_page = canvas["items"][0]
    assert ann_page["id"] == "http://iiif.example.com/manifest/object/123/image/0/canvas/page"
    assert ann_page["type"] == "AnnotationPage"
    assert "items" in ann_page
    assert isinstance(ann_page["items"], list)
    assert len(ann_page["items"]) == 1
    ann = ann_page["items"][0]
    assert ann["id"] == "http://iiif.example.com/manifest/object/123/image/0/canvas/annotation"
    assert ann["type"] == "Annotation"
    assert ann["motivation"] == "painting"
    body = ann["body"]
    assert body["id"] == "https://iiif.example/img.jpg/full/max/0/default.jpg"
    assert body["type"] == "Image"
    assert body["height"] == 800
    assert body["width"] == 1000
    assert "service" in body
    assert isinstance(body["service"], list)
    assert len(body["service"]) == 1
    body_svc = body["service"][0]
    assert body_svc["id"] == "https://iiif.example/img.jpg"
    assert body_svc["type"] == "ImageService3"
    assert body_svc["profile"] == "level2"
    assert body["format"] == "image/jpeg"
    assert ann["target"] == "http://iiif.example.com/manifest/object/123/image/0/canvas"


def test_manifest_500_from_backend(client):
    r = client.get("/manifest/nonexistent_type/nonexistent_id")
    assert r.status_code == 500