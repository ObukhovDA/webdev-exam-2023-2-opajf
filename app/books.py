from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import db, app
from models import Book, Genre, Book_Genre, Cover, Review
from tools import CoverSaver
from flask_login import login_required
from auth import check_rights
import os, bleach

bp = Blueprint('books', __name__, url_prefix='/books')

BOOK_PARAMS = [
    'title', 'description', 'creation_year', 'publisher', 'author', 'page_number', 'cover_id'
]

def params():
    return { p: request.form.get(p) for p in BOOK_PARAMS }

@bp.route('/create', methods=['GET','POST'])
@login_required
@check_rights('create_book')
def create():
        if request.method == 'POST':
            try:
                params_from_form = params()
                for param in params_from_form:
                    param = bleach.clean(param)
                
                book = Book(**params_from_form)

                cover = request.files.get('cover')
                if cover and cover.filename:
                    cover = CoverSaver(cover).save()
                    if cover is None:
                        return(redirect(url_for('index')))
                    book.cover_id = cover.id

                db.session.add(book)
                db.session.commit()

                genres = request.form.getlist('genre')

                for genre in genres:
                    db.session.add(Book_Genre(book_id = book.id,genre_id = genre))
                db.session.commit()

                flash(f'Информация о книге "{book.title}" успешно добавлена', 'success')
                return redirect(url_for('index'))
            except:
                db.session.rollback()
                flash('При сохранении возникла ошибка', 'danger')
                return redirect(url_for('index'))

        try:
            genres = db.session.execute(db.select(Genre)).scalars()
            return render_template('books/add.html',genres=genres)
        except:
            db.session.rollback()
            flash('Ошибка при отображении данных', 'danger')
            return redirect(url_for('index'))

@bp.route('/info/<int:book_id>')
def info(book_id):
    try:
        book = db.session.query(Book).get(book_id)
        reviews = db.session.execute(db.select(Review).filter(Review.book_id == book_id)).scalars()
        return render_template('books/info.html', book=book, reviews=reviews)
    except:
        flash('Ошибка при загрузке данных', 'danger')
        return redirect(url_for('index'))

@bp.route('/edit/<int:book_id>', methods=['GET','POST'])
@login_required
@check_rights('edit_book')
def edit(book_id):
        if request.method == 'POST':
            try:
                params_from_form = params()
                for param in params_from_form:
                    param = bleach.clean(param)
                book = db.session.execute(db.select(Book).filter(Book.id == book_id)).scalar()

                params_from_form['cover_id'] = book.cover_id
                db.session.query(Book).filter(Book.id == book_id).update(params_from_form)

                db.session.query(Book_Genre).filter(Book_Genre.book_id == book_id).delete()
                
                db.session.commit()
                
                genres = request.form.getlist("genre")
                
                for genre in genres:
                    db.session.add(Book_Genre(book_id = book.id, genre_id = genre))
                db.session.commit()

                flash('Информация о книге успешно изменена','success')
                return redirect(url_for('index'))
            except:
                db.session.rollback()
                flash('Ошибка при сохранении изменений', 'danger')
                return redirect(url_for('index'))
            
        try:
            book = db.session.execute(db.select(Book).filter(Book.id == book_id)).scalar()
            genres = db.session.execute(db.select(Genre)).scalars()
            return render_template('books/edit.html', book = book, genres=genres)
        except:
            flash('Ошибка при отображении данных', 'danger')
            return redirect(url_for('index'))
          
@bp.route('/delete/<int:book_id>', methods=['POST'])
@login_required
@check_rights('delete_book')
def delete(book_id):
    try:
        book = db.session.execute(db.select(Book).filter(Book.id == book_id)).scalar()
        if db.session.query(Book).filter(Book.cover_id == book.cover_id).count() < 2:
            cover = db.session.execute(db.select(Cover).filter(Cover.id == book.cover_id)).scalar()
            os.remove(
            os.path.join(app.config['UPLOAD_FOLDER'],
                            cover.storage_filename))
            db.session.query(Cover).filter(Cover.id == book.cover_id).delete()
                        
        db.session.query(Book).filter(Book.id == book_id).delete()
        db.session.commit()
        flash('Информация о книге удалена', 'success')
        return redirect(url_for('index'))
    except:
        db.session.rollback()
        flash('Ошибка при удалении', 'danger')
        return redirect(url_for('index'))

        



