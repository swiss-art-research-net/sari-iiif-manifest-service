FROM python:3.8

RUN apt-get -qq update && \
    apt-get -q -y upgrade && \
    apt-get install -y sudo curl wget locales && \
    rm -rf /var/lib/apt/lists/*
RUN locale-gen en_US.UTF-8

# Install Python packages
RUN pip install fastapi "uvicorn[standard]" sparqlwrapper pydantic

# Prepare directories and volumes
RUN mkdir /scripts
RUN mkdir /config
WORKDIR /scripts

VOLUME /config

# Run idling
ENTRYPOINT tail -f /dev/null