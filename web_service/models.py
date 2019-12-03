from config import db, ma


class File(db.Model):
    __tablename__ = "file_data"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    file_name = db.Column(db.String, nullable=False)
    file_type = db.Column(db.String)
    file_size = db.Column(db.Integer, nullable=False)
    md5 = db.Column(db.String, nullable=False)
    sha1 = db.Column(db.String, nullable=False)


class FileSchema(ma.ModelSchema):
    class Meta:
        model = File
        sql_session = db.session
