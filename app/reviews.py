from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import db
from models import Book, Review
from flask_login import login_required, current_user

import bleach

bp = Blueprint('reviews', __name__, url_prefix='/reviews')

REVIEW_PARAMS = [
    'rating', 'text'
]

def params():
    return { p: request.form.get(p) for p in REVIEW_PARAMS }

@bp.route('/create/<int:book_id>', methods=['GET', 'POST'])
@login_required
def create(book_id):
    if request.method == 'GET':
        try:
            if current_user.can_write_review(book_id):
                book = Book.query.filter_by(id=book_id).scalar()
                return render_template('reviews/add.html', book=book)
            else:
                flash('Вы уже оставляли рецензию на данную книгу', 'warning')
                return redirect(url_for('index'))
        except:
            flash('Ошибка при отображении данных', 'danger')
            return redirect(url_for('index'))
    if request.method == 'POST':
        try:
            params_from_form = params()
            for param in params_from_form:
                param = bleach.clean(param)
            print(params_from_form)
            review = Review(
                book_id = book_id,
                user_id = current_user.id,
                rating = params_from_form['rating'],
                text = params_from_form['text']
            )
            db.session.add(review)
            db.session.commit()
            flash('Рецензия на книгу успешно добавлена', 'success')
            return redirect(url_for('books.info', book_id=book_id))
        except:
            flash('Ошибка при сохранении', 'danger')
            return redirect(url_for('index'))
        


