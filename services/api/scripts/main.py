import os
import yaml
from typing import Union
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from lib.IiifManifestGenerator import IiifManifestGenerator
from lib.DataConnector import FieldConnector

app = FastAPI()

# Inititialise parameters
SPARQL_ENDPOINT = os.environ['SPARQL_ENDPOINT']
NAMESPACE_ENTITIES = os.environ['NAMESPACE_ENTITIES']
NAMESPACE_MANIFESTS = os.environ['NAMESPACE_MANIFESTS']
FIELD_DEFINITIONS_YML = os.environ['FIELD_DEFINITIONS_YML']

manifest = IiifManifestGenerator(baseUri=NAMESPACE_MANIFESTS)
connector = FieldConnector(sparqlEndpoint=SPARQL_ENDPOINT)

# Load field definitions
connector.loadFieldDefinitionsFromFile(FIELD_DEFINITIONS_YML)

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
    subject = f"{NAMESPACE_ENTITIES}{type}/{id}"
    manifestId = f"{type}/{id}"
    label, metadata, images = _getDataForSubject(subject)
    return manifest.generate(id=manifestId, label=label, images=images, metadata=metadata)

def _getDataForSubject(subject: str) -> dict:
    label = connector.getLabelForSubject(subject)
    metadata = connector.getMetadataForSubject(subject)
    images = []
    return label, metadata, images