FROM python:3.11-slim

WORKDIR /home/app/

COPY ./stock/requirements.txt .

RUN pip install -r requirements.txt

COPY ./stock /src
COPY ./backend /src/backend

EXPOSE 5000