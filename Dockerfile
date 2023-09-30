FROM python:3.10.4-slim-bullseye
RUN apt update && apt upgrade -y

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1

WORKDIR /opt/app/

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000