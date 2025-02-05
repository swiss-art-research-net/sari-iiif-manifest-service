"""
Class that provides the application logic for the IIIF Manifest Service API

Usage:
    api = Api(configYmlPath="config.yml", sparqlEndpoint="http://example.org/sparql")
    manifest = api.getManifest(type="example", id="123")
"""

import os
import yaml
import sys

from lib.Cache import Cache
from lib.DataConnector import FieldConnector
from lib.IiifManifestGenerator import IiifManifestGenerator

cache = Cache('/cache')
class Api:

    def __init__(self, configYmlPath: str, sparqlEndpoint: str):
        # Read the configuration YAML file
        with open(configYmlPath, 'r') as f:
            self.config = yaml.safe_load(f)

        required = {
            "fieldDefinitionsFile": "string",
            "cache": {
                "expiration": "string"
            },
            "namespaces": {
                "entities": "string",
                "manifests": "string"
            },
            "queries": {
                "label": "string",
                "images": "string"
            }
        }

        # Check that the configuration file contains the required parameters
        for key in required.keys():
            if key not in self.config.keys():
                print(f"Error: Missing required parameter '{key}' in configuration file '{configYmlPath}'", file=sys.stderr)
                sys.exit(1)
            if isinstance(required[key], dict):
                for subkey in required[key].keys():
                    if not self.config[key].keys() and subkey not in self.config[key].keys():
                       print(f"Error: Missing required parameter '{key}.{subkey}' in configuration file '{configYmlPath}'", file=sys.stderr)
                       sys.exit(1)

        # Field definitions file is configured using a relative path from the configuration file
        # We need to resolve the absolute path
        self.config['fieldDefinitionsFile'] = os.path.join(os.path.dirname(configYmlPath), self.config['fieldDefinitionsFile'])

        if 'rights' in self.config and 'manifestLicenseQuery' in self.config['rights']:
            manifestLicenseQueryTemplate = self.config['rights']['manifestLicenseQuery']
        else:
            manifestLicenseQueryTemplate = None

        if 'thumbnails' in self.config['queries']:
            thumbnailQueryTemplate = self.config['queries']['thumbnails']
        else:
            thumbnailQueryTemplate = None

        self.manifest = IiifManifestGenerator(baseUri=self.config['namespaces']['manifests'])
        self.connector = FieldConnector(
            sparqlEndpoint=sparqlEndpoint,
            manifestLicenseQueryTemplate=manifestLicenseQueryTemplate,
            labelQueryTemplate=self.config['queries']['label'],
            imageQueryTemplate=self.config['queries']['images'],
            thumbnailQueryTemplate=thumbnailQueryTemplate)
        self.connector.loadFieldDefinitionsFromFile(self.config['fieldDefinitionsFile'])

        cache.setExpiration(self.config['cache']['expiration'])
        

    @cache.cache
    def getManifest(self, *, type: str, id: str) -> dict:
        subject = f"{self.config['namespaces']['entities']}{type}/{id}"
        manifestId = f"{type}/{id}"
        data = self.getDataForSubject(subject)
        return self.manifest.generate(
            id=manifestId,
            label=data['label'],
            images=data['images'],
            metadata=data['metadata'],
            license=data['license'],
            thumbnails=data['thumbnails']
        )

    def getDataForSubject(self, subject: str) -> dict:
        label = self.connector.getLabelForSubject(subject)
        metadata = self.connector.getMetadataForSubject(subject)
        images = self.connector.getImagesForSubject(subject)
        thumbnails = self.connector.getThumbnailsForSubject(subject)
        rights = self.connector.getLicenseForManifest(subject)
        if 'options' in self.config and 'imageMetadata' in self.config['options'] and self.config['options']['imageMetadata']:
            for image in images:
                image['metadata'] = self.connector.getMetadataForSubject(image['image'])
        return {
            "label": label,
            "metadata": metadata,
            "images": images,
            "license": rights,
            "thumbnails": thumbnails
        }