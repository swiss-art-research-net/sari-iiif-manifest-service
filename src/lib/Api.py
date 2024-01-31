import os
import yaml
import sys

from lib.IiifManifestGenerator import IiifManifestGenerator
from lib.DataConnector import FieldConnector

class Api:

    def __init__(self, configYmlPath: str, sparqlEndpoint: str):
        # Read the configuration YAML file
        with open(configYmlPath, 'r') as f:
            self.config = yaml.safe_load(f)

        required = {
            "fieldDefinitionsFile": "string",
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

        self.manifest = IiifManifestGenerator(baseUri=self.config['namespaces']['manifests'])
        self.connector = FieldConnector(sparqlEndpoint=sparqlEndpoint)
        self.connector.loadFieldDefinitionsFromFile(self.config['fieldDefinitionsFile'])

    def getManifest(self, *, type: str, id: str) -> dict:
        subject = f"{self.config['namespaces']['entities']}{type}/{id}"
        manifestId = f"{type}/{id}"
        label, metadata, images = self.getDataForSubject(subject)
        return self.manifest.generate(id=manifestId, label=label, images=images, metadata=metadata)

    def getDataForSubject(self, subject: str) -> dict:
        label = self.connector.getLabelForSubject(subject)
        metadata = self.connector.getMetadataForSubject(subject)
        images = self.connector.getImagesForSubject(subject)
        return label, metadata, images