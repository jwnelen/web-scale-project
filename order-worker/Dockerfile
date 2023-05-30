FROM python:3.11-slim

WORKDIR /home/app/

COPY ./order-worker/requirements.txt .

RUN pip install -r requirements.txt

COPY ./order-worker/ src/
COPY ./backend/ src/backend/

EXPOSE 5002