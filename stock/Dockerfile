FROM python:3.11-slim

WORKDIR /home/flask-app/

COPY ./stock/requirements.txt .

RUN pip install -r requirements.txt

COPY ./stock /stock
COPY ./backend /stock/backend

EXPOSE 5000