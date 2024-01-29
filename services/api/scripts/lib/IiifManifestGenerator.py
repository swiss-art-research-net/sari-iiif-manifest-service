"""
Class for generating IIIF manifests based on data retrieved from a SPARQL endpoint.
Metadata is retrieved from the SPARQL endpoint through the use of field definitions.
"""
from string import Template
from SPARQLWrapper import SPARQLWrapper, JSON
class IiifManifestGenerator:

    def __init__(self, *, sparqlEndpoint: str, fields: dict, namespaces: dict = {}, baseUri: str = "http://example.org/manifests/"):
        """
        Initialize the generator.
        :param sparqlEndpoint: The SPARQL endpoint to query.
        """
        self.sparqlEndpoint = sparqlEndpoint
        self.fields = fields
        self.namespaces = namespaces
        self.baseUri = baseUri

        sparql = SPARQLWrapper(self.sparqlEndpoint)
        sparql.setReturnFormat(JSON)
        self.sparql = sparql
        # Test connection
        self.sparql.setQuery("SELECT ?s ?p ?o WHERE {?s ?p ?o} LIMIT 1")
        try:
            self.sparql.query().convert()
        except:
            raise Exception("Could not connect to SPARQL endpoint.")


    def generate(self, *, subject: str) -> dict:
        manifest = {
            "@context": "http://iiif.io/api/presentation/3/context.json",
            "id": self.baseUri,
            "items": [],
            "type": "Manifest",
            "label": {
                "none": ["Placeholder label"]
            },
            "metadata": self.getMetadataForSubject(subject)
        }
        return manifest
    
    def getMetadataForSubject(self, subject: str) -> dict:
        metadata = []
    
        labelQueryTemplate = Template("""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?label (LANG(?label) as ?language WHERE {
                <$uri> rdfs:label ?label .
            }
        """)

        namespaces = ""
        for prefix, namespace in self.namespaces.items():
            namespaces += "PREFIX " + prefix + ": <" + namespace + ">\n"
        
        for field in self.fields.values():
            query = namespaces + field['query'].replace("$subject", "<%s>" % subject)
            self.sparql.setQuery(query)
            try:
                result = self._sparqlResultToDict(self.sparql.query().convert())
            except:
                raise Exception("Could not execute query: %s" % query)

            if result:
                # might be several values
                valueLabels = []
                for row in result:
                    value = row['value']
                    if not 'label' in result and field['datatype'] == 'xsd:anyURI':
                        self.sparql.setQuery(labelQueryTemplate.substitute(uri=value))
                        labelResult = self._sparqlResultToDict(self.sparql.query().convert())
                        try:
                            label = labelResult[0]['label']
                        except:
                            label = False
                    else:
                        label = result[0]['value']
                    valueLabels.append(label)
                metadata.append({
                    "label": {
                        "none": [field['label']]
                    },
                    "value": {
                        "none": [', '.join(valueLabels)]
                    }
                })
        return metadata
    
    def _sparqlResultToDict(self, results):
        rows = []
        for result in results["results"]["bindings"]:
            row = {}
            for key in list(result.keys()):
                row[key] = result[key]["value"]
            rows.append(row)
        return rows