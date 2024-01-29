"""
Class for generating IIIF manifests based on data retrieved from a SPARQL endpoint.
Metadata is retrieved from the SPARQL endpoint through the use of field definitions.
"""

class IiifManifestGenerator:

    def __init__(self, *, sparqlEndpoint: str):
        """
        Initialize the generator.
        :param sparqlEndpoint: The SPARQL endpoint to query.
        """
        self.sparqlEndpoint = sparqlEndpoint

    def generate(self, *, subject: str, fields: dict, namespaces: dict = {}) -> dict:
        return {
            "result": "success",
            "subject": subject,
            "fields": fields
        }