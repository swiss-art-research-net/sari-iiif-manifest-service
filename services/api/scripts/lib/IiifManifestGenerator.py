"""
Class for generating IIIF manifests based on data retrieved from a SPARQL endpoint.
Metadata is retrieved from the SPARQL endpoint through the use of field definitions.
"""
from string import Template
class IiifManifestGenerator:

    def __init__(self, *, baseUri: str = "http://example.org/manifests/"):
        """
        Initialize the generator.
        """
        self.baseUri = baseUri

    def generate(self, *, id: str, images: list, metadata: list) -> dict:
        manifest = {
            "@context": "http://iiif.io/api/presentation/3/context.json",
            "id": f"{self.baseUri}{id}",
            "items": [],
            "type": "Manifest",
            "label": {
                "none": ["Placeholder label"]
            },
            "metadata": metadata
        }
        return manifest