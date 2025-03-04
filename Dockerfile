FROM python:3.8

RUN apt-get -qq update && \
    apt-get -q -y upgrade && \
    apt-get install -y sudo curl wget locales && \
    rm -rf /var/lib/apt/lists/*
RUN locale-gen en_US.UTF-8

# Install Python packages
RUN pip install fastapi "uvicorn[standard]" sparqlwrapper iiif-prezi3

# Add scripts
ADD ./src /src
ADD ./config /config

# Prepare directories and volumes
RUN mkdir /cache
WORKDIR /src

VOLUME /config
VOLUME /cache

EXPOSE 8080

# Run idling
ENTRYPOINT uvicorn main:app --host 0.0.0.0 --port 8080