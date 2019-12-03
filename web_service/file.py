from flask import abort, make_response, request
from config import db, app
from models import File, FileSchema
import hashlib
import json
from urllib.parse import urljoin
from requests import get
# from server import logger
import psycopg2
import os
import getpass as gp
import configparser

from werkzeug.utils import secure_filename


def read_all():
    file = File.query.order_by(File.id).all()

    file_schema = FileSchema(many=True)
    data = file_schema.dump(file)
    return data


def read_md5(md5):

    file = (
        File.query.filter(File.md5 == md5)
            .one_or_none()
    )

    if file is not None:
        file_schema = FileSchema()
        data = file_schema.dump(file)
        return data

    else:
        abort(
            404, "File with the MD5 hash {md5} not found".format(md5=md5)
        )


def read_sha1(sha1):

    file = (
        File.query.filter(File.sha1 == sha1)
            .one_or_none()
    )

    if file is not None:
        file_schema = FileSchema()
        data = file_schema.dump(file)
        return data

    else:
        abort(
            404, "File with the SHA1 hash {sha1} not found".format(sha1=sha1)
        )


def upload():
    file = request.files['files']
    filename = secure_filename(file.filename)
    folder = app.config['UPLOAD_FOLDER']
    file_path = os.path.join(folder, filename)
    file.save(file_path)
    meta_data = extract_data(filename, file_path)
    create(json.loads(meta_data))
    return 200


def create(file):
    # insert meta_data to web_service_db
    file_name = file["file_name"]
    file_type = file["file_type"]
    file_size = file["file_size"]
    md5 = file["md5"]
    sha1 = file["sha1"]

    schema = FileSchema()
    new_file = schema.load(file, session=db.session)

    db.session.add(new_file)
    db.session.commit()

    data = schema.dump(new_file)

    return data, 201


def update_md5(md5, file):
    update_file = File.query.filter(
        File.md5 == md5
    ).one_or_none()

    if update_file is not None:
        schema = FileSchema()
        up = schema.load(file, session=db.session)
        up.md5 = update_file.md5

        db.session.merge(up)
        db.session.commit()
        data = schema.dump(update_file)

        return data, 200
    else:
        abort(404, f"File not found for MD5 has: {md5}")


def delete_md5(md5):
    file = File.query.filter(File.md5 == md5).one_or_none()
    schema = FileSchema()
    result = schema.dump(file)
    if file is not None:
        filename = f"{result['file_name']}.{result['file_type']}"
        folder = app.config['UPLOAD_FOLDER']
        file_path = os.path.join(folder, filename)
        os.remove(file_path)

        db.session.delete(file)
        db.session.commit()
        return make_response(f"File with MD5 hash {md5} deleted.", 200)
    else:
        abort(404, f"File not found with MD5 hash: {md5}")


def update_sha1(sha1, file):
    update_file = File.query.filter(
        File.sha1 == sha1
    ).one_or_none()

    if update_file is not None:
        schema = FileSchema()
        up = schema.load(file, session=db.session)
        up.sha1 = update_file.sha1

        db.session.merge(up)
        db.session.commit()
        data = schema.dump(update_file)

        return data, 200
    else:
        abort(404, f"File not found for SHA1 has: {sha1}")


def delete_sha1(sha1):
    file = File.query.filter(File.sha1 == sha1).one_or_none()
    schema = FileSchema()
    res = schema.dump(file)
    if file is not None:
        filename = f"{res['file_name']}.{res['file_type']}"
        folder = app.config['UPLOAD_FOLDER']
        file_path = os.path.join(folder, filename)
        os.remove(file_path)

        db.session.delete(file)
        db.session.commit()
        return make_response(f"File with SHA1 hash {sha1} deleted.", 200)
    else:
        abort(404, f"File not found with SHA1 hash: {sha1}")


def extract_data(name, path):

    meta_data = {"file_name": name.split('.')[0],
                 "file_type": name.split('.')[1],
                 "file_size": os.path.getsize(path),
                 "md5": hash_file(path, 'md5'),
                 "sha1": hash_file(path, 'sha1')}
    meta_data = json.dumps(meta_data)
    return meta_data


def hash_file(file, algorithm):
    """ Hash the file using MD5 algorithm. """
    if algorithm == 'md5':
        hasher = hashlib.md5()
        result = 'md5'
    elif algorithm == 'sha1':
        hasher = hashlib.sha1()
        result = 'sha1'
    blocksize = 65536

    with open(file, 'rb') as f:
        buf = f.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(blocksize)
    result = hasher.hexdigest()
    return result
