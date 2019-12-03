FROM python:3

RUN mkdir -p /app
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8000

CMD ["gunicorn", "server:app", "-b", "0.0.0.0:8000"]