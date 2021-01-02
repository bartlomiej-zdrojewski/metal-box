FROM service_base:latest
WORKDIR /authorization_service

ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 8083

COPY ./authorization_service /authorization_service
COPY /db /authorization_service/db

RUN pip install -r requirements.txt

CMD ["flask", "run", "--cert", "adhoc"]
