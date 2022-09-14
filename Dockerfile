# Container image that runs your code
FROM python:3.8

#install pre-requisites
RUN apt-get update \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache-dir --upgrade pip==22.2.2

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY entrypoint.py /entrypoint.py

COPY requirements.txt /requirements.txt

RUN chmod +x /entrypoint.py

WORKDIR /

RUN pip install --no-cache-dir -r requirements.txt

# Code file to execute when the docker container starts up (`entrypoint.py`)
ENTRYPOINT ["/entrypoint.py"]

