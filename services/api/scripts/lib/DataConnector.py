import os
import yaml
from SPARQLWrapper import SPARQLWrapper, JSON
from pydantic import BaseModel

from string import Template
class FieldConnector:

    def __init__(self, *, sparqlEndpoint: str):
        self.endpoint = sparqlEndpoint
        self.fields = {}
        self.namespaces = {}

        # Test connection
        self.sparql = SPARQLWrapper(self.endpoint)
        self.sparql.setReturnFormat(JSON)
        self.sparql.setQuery("SELECT ?s ?p ?o WHERE {?s ?p ?o} LIMIT 1")
        try:
            self.sparql.query().convert()
        except:
            raise Exception("Could not connect to SPARQL endpoint.")

    def loadFieldDefinitionsFromFile(self, inputFile: str):
        if os.path.isfile(inputFile):
            with open(inputFile, 'r') as stream:
                try:
                    fieldDefinitions = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
        if fieldDefinitions:
            for d in fieldDefinitions['fields']:
                self.fields[d['id']] = {
                    "label": d['label'],
                    "datatype": d['datatype'],
                    "query": [query['select'] for query in d['queries'] if 'select' in query ][0]
                }
            self.namespaces = fieldDefinitions['namespaces']

    def getLabelForSubject(self, subject: str) -> str:
        labelQueryTemplate = Template("""
            PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            SELECT ?label WHERE {
                {
                    <$uri> skos:prefLabel ?l1 .
                } UNION {
                    <$uri> rdfs:label ?l2.
                } UNION {
                    <$uri> crm:P190_has_symbolic_content ?l3 .
                } UNION {
                    <$uri> crm:P90_has_value ?l4 .
                }
                BIND(COALESCE(?l1, ?l2, ?l3, ?l4) AS ?label)
            } LIMIT 1
        """)

        self.sparql.setQuery(labelQueryTemplate.substitute(uri=subject))
        result = self._sparqlResultToDict(self.sparql.query().convert())
        return result[0]['label']
    
    def getMetadataForSubject(self, subject: str) -> dict:
        metadata = []

        namespaces = ""
        for prefix, namespace in self.namespaces.items():
            namespaces += "PREFIX " + prefix + ": <" + namespace + ">\n"
        
        for field in self.fields.values():
            query = namespaces + field['query'].replace("$subject", "<%s>" % subject).replace("?subject", "<%s>" % subject)
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
                        label = self.getLabelForSubject(value)
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