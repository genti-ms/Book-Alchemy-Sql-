import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from data_models import db, Author, Book

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'data', 'library.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db.init_app(app)

@app.route('/')
def home():
    sort_by = request.args.get('sort', 'title')
    search_query = request.args.get('q', '')

    books_query = Book.query.join(Author)

    if search_query:
        books_query = books_query.filter(Book.title.ilike(f'%{search_query}%'))

    if sort_by == 'author':
        books = books_query.order_by(Author.name).all()
    else:
        books = books_query.order_by(Book.title).all()

    if search_query and not books:
        flash(f'No books found for search term: "{search_query}"')

    return render_template('home.html', books=books, search_query=search_query, sort_by=sort_by)

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form['name']
        birth_date_str = request.form['birthdate']
        date_of_death_str = request.form.get('date_of_death')

        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()

        date_of_death = None
        if date_of_death_str:
            date_of_death = datetime.strptime(date_of_death_str, '%Y-%m-%d').date()

        author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(author)
        db.session.commit()

        flash(f'Author "{name}" added successfully.')
        return redirect(url_for('add_author'))

    return render_template('add_author.html')

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    authors = Author.query.order_by(Author.name).all()

    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        publication_year = request.form['publication_year']
        author_id = request.form['author_id']

        # Check if ISBN already exists
        existing_book = Book.query.filter_by(isbn=isbn).first()
        if existing_book:
            flash(f'A book with ISBN "{isbn}" already exists. Please use a different ISBN.')
            return redirect(url_for('add_book'))

        book = Book(isbn=isbn, title=title, publication_year=publication_year, author_id=author_id)
        db.session.add(book)
        db.session.commit()

        flash(f'Book "{title}" added successfully.')
        return redirect(url_for('add_book'))

    return render_template('add_book.html', authors=authors)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    author = Author.query.get(book.author_id)

    db.session.delete(book)
    db.session.commit()

    other_books = Book.query.filter_by(author_id=author.id).count()
    if other_books == 0:
        db.session.delete(author)
        db.session.commit()
        flash(f'Book "{book.title}" and author "{author.name}" deleted.')
    else:
        flash(f'Book "{book.title}" deleted.')

    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5002, debug=True)
