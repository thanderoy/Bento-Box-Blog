FROM python:3.10
RUN apt-get update

ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1

WORKDIR /django

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
