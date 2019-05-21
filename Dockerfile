FROM ubuntu:18.10

RUN apt update && apt upgrade -y && apt install -y \
    curl \
    git \
    python3-pip \
    zip

RUN pip3 install -U setuptools pip

COPY . /app/
WORKDIR /app
RUN python3 setup.py install

EXPOSE 5000

ENV LANG=en_US.UTF-8

CMD ["seqrepo-rest-service"]
