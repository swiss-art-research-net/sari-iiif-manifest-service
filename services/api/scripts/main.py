import os
from typing import Union
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from lib.IiifManifestGenerator import IiifManifestGenerator

app = FastAPI()

# Read endpoint from environment variable
sparqlEndpoint = os.environ['SPARQL_ENDPOINT']

manifest = IiifManifestGenerator(sparqlEndpoint=sparqlEndpoint, fieldDefinitions={})

@app.get("/", response_class=HTMLResponse)
def readRoot():
    return """
    <html>
        <head>
            <title>SARI IIIF Manifest Service</title>
        </head>
        <body>
            <h1>SARI IIIF Manifest Service</h1>
            <p>Use the following URL to retrieve a manifest:</p>
            <pre>/manifest/{item_type}/{item_id}</pre>
        </body>
    </html>"""

@app.get("/manifest/{item_type}/{item_id}")
def getManifest(item_type: str, item_id: str):
    return _getManifest(type=item_type, id=item_id)

def _getManifest(*, type: str, id: str) -> dict:
    return manifest.generate(itemType=type, itemId=id)
