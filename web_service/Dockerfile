FROM python:3

RUN mkdir -p /app
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN python build_db.py
RUN python migrate.py db init
RUN python migrate.py db migrate
RUN python migrate.py db upgrade

EXPOSE 8000

CMD ["gunicorn", "server:app", "-b", "0.0.0.0:8000"]