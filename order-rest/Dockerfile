FROM python:3.11-slim

WORKDIR /home/app/

COPY ./order/requirements.txt .

RUN pip install -r requirements.txt

COPY ./order /src
COPY ./backend /src/backend

EXPOSE 5000