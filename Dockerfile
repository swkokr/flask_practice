FROM python:3.9

WORKDIR /flaskAPI

#ADD . /flaskAPI

RUN pip install -r requirements.txt

ENTRYPOINT [ "gunicorn" ]

CMD ["-b", "0.0.0.0:5000", "wsgi:app"]