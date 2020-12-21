FROM python:3.7-alpine
WORKDIR /courier_service

ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 8081

COPY ./courier_service /courier_service
COPY ./dto /courier_service/dto

RUN apk add --no-cache gcc musl-dev linux-headers openssl-dev libffi-dev
RUN pip install -r requirements.txt

CMD ["flask", "run", "--cert", "adhoc"]
