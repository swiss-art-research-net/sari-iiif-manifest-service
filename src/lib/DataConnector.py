"""
Class to query data from a SPARQL endpoint based on field definitions.
The field definitions should be defined in the format of the sari-field-definitions-generator (https://github.com/swiss-art-research-net/sari-field-definitions-generator).

The class uses default query templates to retrieve images and labels. These can be overwritten by providing custom templates.

Example:
    connector = FieldConnector(sparqlEndpoint="http://blazegraph:8080/blazegraph/sparql")
    connector.loadFieldDefinitionsFromFile("fieldDefinitions.yml")

    images = connector.getImagesForSubject("http://example.com/object/123")
    metadata = connector.getMetadataForSubject("http://example.com/object/123")
    label = connector.getLabelForSubject("http://example.com/object/123")

Methods:

    loadFieldDefinitionsFromFile(inputFile: str)
        Load field definitions from a YAML file.

    getImagesForSubject(subject: str) -> list
        Get images for a given URI.

    getLabelForSubject(subject: str) -> str
        Get label for a URI.

    getMetadataForSubject(subject: str) -> dict
        Get the values for all fields for a given URI.

    setLabelQueryTemplate(template: str)
        Set the template for the label query. Provide a SPARQL SELECT query with a $subject placeholder and a ?label variable.

    setImageQueryTemplate(template: str)
        Set the template for the image query. Provide a SPARQL SELECT query with a $subject placeholder and ?image, ?width, and ?height variables.       
"""

import os
import yaml
from SPARQLWrapper import SPARQLWrapper, JSON

from string import Template
class FieldConnector:

    LABEL_QUERY = """
            PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            SELECT ?label WHERE {
                {
                    $subject skos:prefLabel ?l1 .
                } UNION {
                    $subject rdfs:label ?l2.
                } UNION {
                    $subject crm:P190_has_symbolic_content ?l3 .
                } UNION {
                    $subject crm:P90_has_value ?l4 .
                }
                BIND(COALESCE(?l1, ?l2, ?l3, ?l4) AS ?label)
            } LIMIT 1
        """
    
    IMAGE_QUERY = """
            PREFIX aat: <http://vocab.getty.edu/aat/>
            PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
            PREFIX la: <https://linked.art/ns/terms/>
            SELECT ?image ?width ?height WHERE {
                $subject crm:P138i_has_representation?/la:digitally_shown_by ?imageObject .
                ?imageObject la:digitally_available_via/la:access_point ?image ;
                    crm:P43_has_dimension ?dimWidth ;
                    crm:P43_has_dimension ?dimHeight .
                ?dimWidth crm:P2_has_type aat:300055647 ;
                    crm:P90_has_value ?width .
                ?dimHeight crm:P2_has_type aat:300055644 ;
                    crm:P90_has_value ?height .
            }
        """

    def __init__(self, *, 
                 sparqlEndpoint: str, 
                 labelQueryTemplate=LABEL_QUERY, 
                 imageQueryTemplate=IMAGE_QUERY, 
                 thumbnailQueryTemplate=None
        ):
        self.endpoint = sparqlEndpoint
        self.fields = {}
        self.namespaces = {}
        self.labelQueryTemplate = labelQueryTemplate
        self.imageQueryTemplate = imageQueryTemplate
        self.thumbnailQueryTemplate = thumbnailQueryTemplate

        # Test connection
        self.sparql = SPARQLWrapper(self.endpoint)
        self.sparql.setReturnFormat(JSON)
        self.sparql.setQuery("SELECT ?s ?p ?o WHERE {?s ?p ?o} LIMIT 1")
        try:
            self.sparql.query().convert()
        except:
            raise Exception("Could not connect to SPARQL endpoint.")

    def loadFieldDefinitionsFromFile(self, inputFile: str):
        """
        Load field definitions from a YAML file.
        """
        if os.path.isfile(inputFile):
            with open(inputFile, 'r') as stream:
                try:
                    fieldDefinitions = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc, "Could not load field definitions from file '%s'" % inputFile)
        if fieldDefinitions:
            if 'display' in fieldDefinitions:
                fieldsToDisplay = []
                # Create a dictionary for quick lookup
                fieldDict = {field['id']: field for field in fieldDefinitions['fields']}
                fieldsToDisplay = [fieldDict[fieldId] for fieldId in fieldDefinitions['display'] if fieldId in fieldDict]
            else:
                fieldsToDisplay = fieldDefinitions['fields']
            for d in fieldsToDisplay:
                self.fields[d['id']] = {
                    "label": d['label'],
                    "datatype": d['datatype'],
                    "query": [query['select'] for query in d['queries'] if 'select' in query ][0]
                }
            self.namespaces = fieldDefinitions['namespaces']

    def getImagesForSubject(self, subject: str) -> list:
        """
        Get images for a given URI.
        """
        imageQueryTemplate = Template(self.imageQueryTemplate)
        query = imageQueryTemplate.substitute(subject=f"<{subject}>")
        
        self.sparql.setQuery(query)
        try:
            queryResult = self.sparql.query().convert()
        except Exception as e:
            print(e)
            raise Exception("Could not execute query: %s" % query)
        images = self._sparqlResultToDict(queryResult)
        return images
    
    def getLabelForSubject(self, subject: str) -> str:
        """
        Get label for a URI.
        """
        labelQueryTemplate = Template(self.labelQueryTemplate)
        query = labelQueryTemplate.substitute(subject=f"<{subject}>")
        self.sparql.setQuery(query)
        try:
            queryResult = self.sparql.query().convert()
        except Exception as e:
            print(e)
            raise Exception("Could not execute query: %s" % query)
        result = self._sparqlResultToDict(queryResult)
        if len(result) == 0:
            raise Exception("No label found for subject '%s'" % subject)
        return result[0]['label']
    
    def getRightsForSubject(self, subject: str, rightsQueryTemplate: str) -> str:
        """
        Get rights for a URI.
        """
        template = Template(rightsQueryTemplate)
        query = template.substitute(subject=f"<{subject}>")
        self.sparql.setQuery(query)
        try:
            queryResult = self.sparql.query().convert()
        except Exception as e:
            print(e)
            raise Exception("Could not execute query: %s" % query)
        result = self._sparqlResultToDict(queryResult)
        if len(result) == 0:
            return None
        return result[0]['value']
    
    def getRequiredStatementForSubject(self, subject: str, requiredStatementTemplate: str) -> str:
        """
        Get required statement for a Manifest URI.
        """
        template = Template(requiredStatementTemplate)
        query = template.substitute(subject=f"<{subject}>")
        self.sparql.setQuery(query)
        try:
            queryResult = self.sparql.query().convert()
        except Exception as e:
            print(e)
            raise Exception("Could not execute query: %s" % query)
        result = self._sparqlResultToDict(queryResult)
        if len(result) == 0:
            return None
        return result[0]
    
    def getMetadataForSubject(self, subject: str) -> dict:
        """
        Get the values for all fields for a given URI.
        """

        metadata = []
        labelCache = {}
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
                        if value in labelCache:
                            label = labelCache[value]
                        else:    
                            label = self.getLabelForSubject(value)
                            labelCache[value] = label
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
    
    def getThumbnailsForSubject(self, subject: str) -> list:
        """
        Get thumbnails for a given URI.
        """
        if self.thumbnailQueryTemplate is None:
            return []
        thumbnailQueryTemplate = Template(self.thumbnailQueryTemplate)
        query = thumbnailQueryTemplate.substitute(subject=f"<{subject}>")
        
        self.sparql.setQuery(query)
        try:
            queryResult = self.sparql.query().convert()
        except Exception as e:
            print(e)
            raise Exception("Could not execute query: %s" % query)
        thumbnails = self._sparqlResultToDict(queryResult)
        return thumbnails
    
    def setLabelQueryTemplate(self, template: str):
        """
        Set the template for the label query. 
        Provide a SPARQL SELECT query with a $subject placeholder and a ?label variable.
        """
        self.labelQueryTemplate = template

    def setImageQueryTemplate(self, template: str):
        """
        Set the template for the image query.
        Provide a SPARQL SELECT query with a $subject placeholder and ?image, ?width, and ?height variables.
        """
        self.imageQueryTemplate = template
    
    def _sparqlResultToDict(self, results):
        """
        Convert SPARQL results to a list of dictionaries.
        """
        rows = []
        for result in results["results"]["bindings"]:
            row = {}
            for key in list(result.keys()):
                row[key] = result[key]["value"]
            rows.append(row)
        return rows