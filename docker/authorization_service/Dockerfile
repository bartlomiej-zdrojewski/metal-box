FROM python:3.7-alpine
WORKDIR /authorization_service

ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 8083

COPY ./authorization_service /authorization_service
COPY ./dto /authorization_service/dto

RUN apk add --no-cache gcc musl-dev linux-headers openssl-dev libffi-dev
RUN pip install -r requirements.txt

CMD ["flask", "run", "--cert", "adhoc"]
