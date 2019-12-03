import os
from connexion import App
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

basedir = os.path.abspath(os.path.dirname(__file__))

conn = App(__name__, specification_dir='./')

app = conn.app

# postgres_url = 'postgres://127.0.0.1:5433/web_service_db?user=postgres&password=password'
postgres_url = 'postgres://postgres:docker@127.0.0.1:54320/web_service_db'

app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = postgres_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = basedir+"\\web_service_disk\\"

db = SQLAlchemy(app)

ma = Marshmallow(app)
