from flask import Flask, render_template, request, send_from_directory, flash
from sqlalchemy import MetaData, desc
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import math
from flaskext.markdown import Markdown

app = Flask(__name__)
Markdown(app)

application = app

app.config.from_pyfile('config.py')

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)

from auth import bp as auth_bp, init_login_manager
from books import bp as books_bp
from reviews import bp as reviews_bp


app.register_blueprint(auth_bp)
app.register_blueprint(books_bp)
app.register_blueprint(reviews_bp)


init_login_manager(app)

from models import Book, Cover

@app.route('/')
def index():
    try:
        BOOKS_PER_PAGE = 4
        page = request.args.get('page', 1, type=int)

        books = db.session.execute(db.select(Book).order_by(desc(Book.creation_year)).limit(BOOKS_PER_PAGE).offset(BOOKS_PER_PAGE * (page - 1))).scalars()

        page_count = math.ceil(db.session.query(Book).count() / BOOKS_PER_PAGE) or 1
                
        return render_template(
            'index.html',
            books = books,
            page = page,
            page_count = page_count,
        )
    except:
        flash("Ошибка при загрузке данных",'danger')
        return render_template(
            'index.html',
            books = [],
            page = 1,
            page_count = 1,
        )

@app.route('/covers/<cover_id>')
def cover(cover_id):
    img = db.get_or_404(Cover, cover_id)
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               img.storage_filename)
