FROM python:3.9

WORKDIR /flaskAPI

ADD . /flaskAPI

RUN pip install -r requirements.txt
