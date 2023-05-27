FROM python:3.11-slim

WORKDIR /home/app/

COPY ./payment/requirements.txt .

RUN pip install -r requirements.txt

COPY ./payment /src
COPY ./backend /src/backend

EXPOSE 5000