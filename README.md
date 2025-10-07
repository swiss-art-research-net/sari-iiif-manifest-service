# SARI IIIF Manifest Service

## About

A service to generate and serve IIIF Manifests based on data stored in a RDF triplestore.

### Features

* Generates IIIF Manifests based on data stored in a RDF triplestore
* Supports ResearchSpace/Metaphacts [Field Definitions](https://github.com/swiss-art-research-net/sari-field-definitions-generator) to retrieve metadata
* Implements [Linked.Art](https://linked.art/) model for IIIF images per default
* File based cache for generated manifests

## How to use

Pre-requisites: [Docker](https://www.docker.com/) (including Docker Compose)

The main configuration is done using the files found in the `./config` directory. These files can be used as a starting point to customise the service. You can either edit the files directly or create a copy of the files.

The config file that the service uses can be specified using the `CONFIG_YML` environment variable. In addition the service expects the URL of a SPARQL endpoint to be specified using the `SPARQL_ENDPOINT` environment variable.

### Configuration

1. Copy the example config file:
    `cp config/default.yml config/config.yml`
1. Copy the example `.env` file:
    `cp .env.example .env`
1. Edit the `.env` file and set the `SPARQL_ENDPOINT` environment variable to the URL of your SPARQL endpoint and the `CONFIG_YML` environment variable to the path of your config file.
1. Edit the `config.yml` file based on the comments in the file.

A default field definitions file is provided. To use your own metadata fields, create a copy of the file and edit it accordingly or use one from an existing project. The path to the field definitions file can be specified in the `config.yml` file.

### Authentication (optional)

The service supports authentication when connecting to protected SPARQL endpoints.  
By default, no authentication is used. It will connect anonymously unless credentials or tokens are provided via environment variables.

To use authentication, set the following variables in your `.env` file as needed:

```bash
# Authentication method: BASIC, DIGEST, or leave empty for none
SPARQL_HTTP_AUTH=BASIC

# Username and password (for BASIC or DIGEST)
SPARQL_USERNAME=myuser
SPARQL_PASSWORD=mypassword

# Alternatively, use a bearer token
SPARQL_BEARER_TOKEN=eyJhbGciOi...

# Optional connection settings
SPARQL_TIMEOUT=30          # request timeout in seconds (default: 30)
SPARQL_REQUEST_METHOD=GET  # or POST
```

### Running the service

Run `docker-compose up -d` to start the service. When using the service in production, comment out the respective lines in the `.env` file.

### Structure of the config file

The config file is a YAML file with the following structure:

```yaml
fieldDefinitionsFile: "path/to/field-definitions.yml"
cache:
    expiration: "1w"
aliases:
    ...
namespaces:
    entities: "https://example.org/"
    manifests: "http://iiif.example.com/manifest/"
queries:
    label: |
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?label WHERE {
            $subject skos:prefLabel ?label .
        } LIMIT 1
    images: |
        SELECT ?image ?width ?height WHERE {
            ...
        }
    thumbnails: |
        SELECT ?thumbnail ?width ?height WHERE {
            ...
        }
rights:
    manifest:
        rightsQuery: |
            SELECT ?value WHERE {
                ...
            }
        requiredStatementQuery: |
            SELECT ?label ?value WHERE {
                ...
            }
    images:
        rightsQuery: |
            SELECT ?value WHERE {
                ...
            }
        requiredStatementQuery: |
            SELECT ?label ?value WHERE {
                ...

options:
    ...
```

For details on the individual config options, please refer to the comments in the `config/default.yml` file.