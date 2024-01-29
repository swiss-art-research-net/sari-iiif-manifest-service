from typing import Union
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def readRoot():
    return {"SARI IIIF Manifest Service": "v0.1"}

@app.get("/manifest/{item_type}/{item_id}")
def getManifest(item_type: str, item_id: str):
    return _getManifest(type=item_type, id=item_id)

def _getManifest(*, type: str, id: str) -> dict:
    return {"type": type, "id": id}