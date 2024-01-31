"""
Entry point for the IIIF Manifest api.

The main configuration is done via a YAML file. The path to the file is passed via the
CONFIG_YML environment variable.

The SPARQL endpoint is passed via the SPARQL_ENDPOINT environment variable.


To run the application, use a command like 'uvicorn main:app'.
"""

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from lib.Api import Api

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
CONFIG_YML = os.environ['CONFIG_YML']

api= Api(CONFIG_YML, SPARQL_ENDPOINT)

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
    return api.getManifest(type=item_type, id=item_id)
