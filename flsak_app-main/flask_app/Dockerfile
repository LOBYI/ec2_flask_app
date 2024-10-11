FROM python:3

ADD . /www
WORKDIR /www

RUN python3 -m pip install -U pip
RUN pip3 install flask
RUN pip3 install python-dotenv
RUN export FLASK_ENV=development
RUN pip install flask-sqlalchemy
RUN apt-get update
RUN apt-get install sqlite3

CMD ["python3",  "-m", "flask",  "run",  "--host=0.0.0.0"]