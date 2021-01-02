FROM python:3.7-alpine

COPY ./db /db

RUN apk add --no-cache gcc musl-dev linux-headers openssl-dev libffi-dev
RUN pip install -r /db/requirements.txt
