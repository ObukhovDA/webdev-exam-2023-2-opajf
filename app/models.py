import os
import sqlalchemy as sa
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from flask import url_for
from app import db
from user_policy import UsersPolicy
from sqlalchemy.sql import func, text

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role_id == 3
    
    def is_moder(self):
        return self.role_id == 2
    
    def can(self, action, record=None):
        users_policy = UsersPolicy(record)
        method = getattr(users_policy, action, None)
        if method:
            return method()
        return False
    
    def can_write_review(self, book_id):
        data = db.session.query(Review).filter(Review.book_id == book_id, Review.user_id == self.id).count()
        if data == 0:
            return True
        else:
            return False

    @property
    def full_name(self):
        return ' '.join([self.last_name, self.first_name, self.middle_name or ''])

    def __repr__(self):
        return '<User %r>' % self.login
    
class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<Role %r>' % self.title

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    creation_year = db.Column(db.Integer, nullable=False)
    publisher = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
    cover_id = db.Column(db.String(250), db.ForeignKey('covers.id'), nullable=False)

    def __repr__(self):
        return '<Book %r>' % self.title
    
    @property
    def cover(self):
        return db.session.execute(db.select(Cover).filter_by(id=self.cover_id)).scalar()

    @property
    def genres(self):
        sql = 'SELECT * FROM genres JOIN books_genres ON books_genres.genre_id = genres.id AND books_genres.book_id = :book_id'
        print(self.id)
        return db.session.execute(text(sql), {'book_id': self.id})
    
    @property
    def rating(self):
        query = db.session.query(func.avg(Review.rating).label('average')).filter(Review.book_id==self.id)
        return db.session.execute(query).scalar()

    
class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)

class Book_Genre(db.Model):
    __tablename__ = 'books_genres'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), nullable=False)
    
class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=sa.sql.func.now())

    def __repr__(self):
        return '<Review %r>' % self.text
    
    def get_author_full_name(self):
        return db.session.execute(db.Select(User).filter_by(id = self.user_id)).scalar().full_name
    
class Cover(db.Model):
    __tablename__ = 'covers'

    id = db.Column(db.String(250), primary_key=True)
    file_name = db.Column(db.String(250), nullable=False)
    MIME = db.Column(db.String(250), nullable=False)
    MD5 = db.Column(db.String(150), nullable=False)
    
    def __repr__(self):
        return '<Cover %r>' % self.file_name

    @property
    def storage_filename(self):
        _, ext = os.path.splitext(self.file_name)
        return self.id + ext

    @property
    def url(self):
        return url_for('cover', cover_id=self.id)