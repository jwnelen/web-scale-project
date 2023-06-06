FROM python:3.11-slim

WORKDIR /home/app/

COPY ./kafka-admin/requirements.txt .

RUN pip install -r requirements.txt

COPY ./kafka-admin/ src/

EXPOSE 5000