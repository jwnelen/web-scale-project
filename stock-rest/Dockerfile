FROM python:3.11-slim

WORKDIR /home/app/

COPY ./stock-rest/requirements.txt .

RUN pip install -r requirements.txt

COPY ./stock-rest/ src/
COPY ./backend/ src/backend/

EXPOSE 5000