# syntax = docker/dockerfile:experimental

# docker build -t biocommons/seqrepo-rest-service .

FROM ubuntu:22.04

RUN apt update && apt upgrade -y && apt install -y \
    curl \
    git \
    python3-pip \
    zip

RUN --mount=type=cache,target=/root/.cache/pip pip3 install -U setuptools pip

COPY . /app/
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/pip pip install -e .

EXPOSE 5000

CMD ["seqrepo-rest-service"]
