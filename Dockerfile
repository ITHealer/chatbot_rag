FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

COPY . .

COPY ./wait-for-postgres.sh ./wait-for-postgres.sh

RUN chmod +x ./wait-for-postgres.sh