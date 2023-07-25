FROM python:3.11

ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.in .

RUN pip install -r requirements.in

COPY . .
