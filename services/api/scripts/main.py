import os
import yaml
from typing import Union
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from lib.IiifManifestGenerator import IiifManifestGenerator

app = FastAPI()

# Read paramaters from environment variables
sparqlEndpoint = os.environ['SPARQL_ENDPOINT']
fieldDefinitionsYml = os.environ['FIELD_DEFINITIONS_YML']
namespace = os.environ['NAMESPACE']

# Read field definitions from YAML file
fieldDefinitions = {}
if os.path.isfile(fieldDefinitionsYml):
    with open(fieldDefinitionsYml, 'r') as stream:
        try:
            fieldDefinitions = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

manifest = IiifManifestGenerator(sparqlEndpoint=sparqlEndpoint)

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
    subject = f"{namespace}{type}/{id}"
    fields = {}
    for d in fieldDefinitions['fields']:
        fields[d['id']] = [query['select'] for query in d['queries']][0]
    return manifest.generate(subject=subject, fields=fields, namespaces=fieldDefinitions['namespaces'])