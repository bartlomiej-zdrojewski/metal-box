FROM service_base:latest
WORKDIR /main_service

ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 8080

COPY ./main_service /main_service
COPY /db /main_service/db

RUN pip install -r requirements.txt

CMD ["flask", "run", "--cert", "adhoc"]
