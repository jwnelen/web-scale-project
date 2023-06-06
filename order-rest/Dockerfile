FROM python:3.11-slim

WORKDIR /home/app/

COPY ./order-rest/requirements.txt .

RUN pip install -r requirements.txt

COPY ./order-rest/ src/
COPY ./backend/ src/backend/

EXPOSE 5002