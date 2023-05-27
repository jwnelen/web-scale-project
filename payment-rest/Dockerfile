FROM python:3.11-slim

WORKDIR /home/app/

COPY ./payment-rest/requirements.txt .

RUN pip install -r requirements.txt

COPY ./payment-rest /src
COPY ./backend /src/backend

EXPOSE 5000