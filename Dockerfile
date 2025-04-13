FROM python:3.11-slim-bullseye AS builder-image

ENV PYTHONUNBUFFERED=1

WORKDIR /code

RUN apt-get update

COPY requirements.txt /code/

RUN pip install -r requirements.txt && \
    pip install unidecode

COPY setup.py /code/setup.py
COPY setup.cfg /code/setup.cfg
COPY versioneer.py /code/versioneer.py
COPY pyproject.toml /code/pyproject.toml
COPY resources/ /code/resources
COPY src /code/src
COPY README.md /code/README.md

RUN pip uninstall -y refined && \
    pip install .

ENTRYPOINT ["refined"]
