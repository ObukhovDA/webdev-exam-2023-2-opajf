import hashlib
import os
from werkzeug.utils import secure_filename
from models import Cover
from app import db, app
import uuid
from flask import flash, redirect, url_for

class CoverSaver:
    def __init__(self, file):
        self.file = file

    def save(self):
        self.img = self.__find_by_md5_hash()
        if self.file.mimetype not in app.config['MIME_TYPES']:
            flash('Обложка должна быть изображением', 'danger')
            return None
        if self.img is not None:
            return self.img
        file_name = secure_filename(self.file.filename)
        self.img = Cover(
            id=str(uuid.uuid4()),
            file_name = file_name,
            MIME = self.file.mimetype,
            MD5 = self.MD5)
        self.file.save(
            os.path.join(app.config['UPLOAD_FOLDER'],
                         self.img.storage_filename))
        db.session.add(self.img)
        db.session.commit()
        return self.img

    def __find_by_md5_hash(self):
        self.MD5 = hashlib.md5(self.file.read()).hexdigest()
        self.file.seek(0)
        return db.session.execute(db.select(Cover).filter(Cover.MD5 == self.MD5)).scalar()