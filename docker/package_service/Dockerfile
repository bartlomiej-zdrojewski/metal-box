FROM service_base:latest
WORKDIR /package_service

ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 8084

COPY ./package_service /package_service
COPY /db /package_service/db

RUN pip install -r requirements.txt

CMD ["flask", "run", "--cert", "adhoc"]
