"""
Entry point for the FastAPI application. Configuration is done via environment variables.

SPARQL_ENDPOINT: 
    The endpoint for the SPARQL service to query data from.

NAMESPACE_ENTITIES: 
    The namespace for entities. This is used to construct the URI for the subject based on 
    a type and ID. For example, for entities of the form 'http://example.com/object/123', 
    the namespace would be 'http://example.com/', the type would be 'object', and the ID
    would be '123'.

NAMESPACE_MANIFESTS:
    The namespace for manifests. This is used to construct the URI for the manifest based
    on a type and ID. For example, for manifests of the form 'http://iiif.example.com/manifest/object/123',
    the namespace would be 'http://iiif.example.com/', the type would be 'object', and the ID

FIELD_DEFINITIONS_YML:
    The path to the YAML file containing field definitions. It uses the sari-field-definitions-generator
    format.

To run the application, use a command like 'uvicorn main:app'.
"""

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from lib.IiifManifestGenerator import IiifManifestGenerator
from lib.DataConnector import FieldConnector

app = FastAPI()

# Allow all origins to access your API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inititialise parameters
SPARQL_ENDPOINT = os.environ['SPARQL_ENDPOINT']
NAMESPACE_ENTITIES = os.environ['NAMESPACE_ENTITIES']
NAMESPACE_MANIFESTS = os.environ['NAMESPACE_MANIFESTS']
FIELD_DEFINITIONS_YML = os.environ['FIELD_DEFINITIONS_YML']

# Initialise manifest generator and data connector
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
    images = connector.getImagesForSubject(subject)
    return label, metadata, images