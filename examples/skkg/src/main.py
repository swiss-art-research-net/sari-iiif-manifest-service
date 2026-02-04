"""
Entry point for the IIIF Manifest api.

The main configuration is done via a YAML file. The path to the file is passed via the
CONFIG_YML environment variable.

The SPARQL endpoint is passed via the SPARQL_ENDPOINT environment variable.


To run the application, use a command like 'uvicorn main:app'.
"""

import os
import yaml
from fastapi import FastAPI, HTTPException
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

# Optional SPARQL authentication settings
SPARQL_HTTP_AUTH = os.getenv("SPARQL_HTTP_AUTH")
SPARQL_USERNAME = os.getenv("SPARQL_USERNAME")
SPARQL_PASSWORD = os.getenv("SPARQL_PASSWORD")
SPARQL_BEARER_TOKEN = os.getenv("SPARQL_BEARER_TOKEN")
SPARQL_TIMEOUT = int(os.getenv("SPARQL_TIMEOUT") or 30)
SPARQL_REQUEST_METHOD = os.getenv("SPARQL_REQUEST_METHOD", "GET").upper()

# Load relevant configuration
with open(CONFIG_YML, 'r') as f:
    config = yaml.safe_load(f)
    aliases = config.get('aliases', [])

api = Api(CONFIG_YML, SPARQL_ENDPOINT, httpAuth=SPARQL_HTTP_AUTH, username=SPARQL_USERNAME, password=SPARQL_PASSWORD, bearerToken=SPARQL_BEARER_TOKEN, timeout=SPARQL_TIMEOUT, requestMethod=SPARQL_REQUEST_METHOD)

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
    try:
        manifest = api.getManifest(type=item_type, id=item_id)
        return manifest
    except Exception as e:
        print(f"Error retrieving manifest for {item_type}/{item_id}: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve manifest. Does the item exist?")

# Register aliases dynamically
for alias in aliases:
    @app.get(f"/{alias}/{{item_type}}/{{item_id}}")
    async def aliasManifest(item_type: str, item_id: str, alias=alias):
        return api.getManifest(type=item_type, id=item_id)
