FROM python:3.11-slim

WORKDIR /home/app/

COPY ./payment-worker/requirements.txt .

RUN pip install -r requirements.txt

COPY ./payment-worker/ src/
COPY ./backend/ src/backend/
COPY ./keyfile.json /tmp/keys/keyfile.json

EXPOSE 5001