FROM python:3.10
RUN apt-get update
RUN apt-get -y install python3-pip python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0

ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1

WORKDIR /django

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .