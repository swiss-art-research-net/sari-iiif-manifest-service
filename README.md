# SARI IIIF Manifest Service

## About

A service to generate and serve IIIF Manifests based on data stored in a RDF triplestore.

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

### Running the service

Run `docker-compose up -d` to start the service. When using the service in production, comment out the respective lines in the `.env` file.