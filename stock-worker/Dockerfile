FROM python:3.11-slim

WORKDIR /home/app/

COPY ./stock-worker/requirements.txt .

RUN pip install -r requirements.txt

COPY ./stock-worker/ src/
COPY ./backend/ src/backend/
COPY ./keyfile.json /tmp/keys/keyfile.json

EXPOSE 5000