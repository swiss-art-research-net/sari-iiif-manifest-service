FROM python:3.10

RUN apt-get -qq update && \
    apt-get -q -y upgrade && \
    apt-get install -y sudo curl wget locales && \
    rm -rf /var/lib/apt/lists/*
RUN locale-gen en_US.UTF-8

# Install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Add scripts and config
ADD ./src /src
ADD ./config.yml /skkg-config/config.yml
ADD ./fieldDefinitions.yml /skkg-config/fieldDefinitions.yml
# Prepare directories and volumes
RUN mkdir /cache
WORKDIR /src

VOLUME /skkg-config
VOLUME /cache

EXPOSE 8080

# Run idling
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
