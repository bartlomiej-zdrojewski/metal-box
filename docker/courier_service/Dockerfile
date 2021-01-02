FROM service_base:latest
WORKDIR /courier_service

ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 8081

COPY ./courier_service /courier_service
COPY /db /courier_service/db

RUN pip install -r requirements.txt

CMD ["flask", "run", "--cert", "adhoc"]
