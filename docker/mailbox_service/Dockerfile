FROM service_base:latest
WORKDIR /mailbox_service

ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 8082

COPY ./mailbox_service /mailbox_service
COPY /db /mailbox_service/db

RUN pip install -r requirements.txt

CMD ["flask", "run", "--cert", "adhoc"]
