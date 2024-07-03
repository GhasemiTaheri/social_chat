FROM python:3.10
LABEL authors="joojoo"


WORKDIR app/

RUN pip install --upgrade pip

COPY . .

RUN pip install -r requirements.txt