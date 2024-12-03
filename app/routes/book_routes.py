from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.book import Book
from app.models.review import Review
from app.models.interaction import ReviewLike
from app.auth import login_required, admin_required
from app import mysql

bp = Blueprint('books', __name__, url_prefix='/books')

@bp.route('/')
def list():
    books = Book.get_all()
    return render_template('books/list.html', books=books)

@bp.route('/create', methods=('GET', 'POST'))
@admin_required
def create():
    if request.method == 'POST':
        book = Book(
            title=request.form['title'],
            author=request.form['author'],
            isbn=request.form['isbn'],
            publisher=request.form['publisher'],
            publication_year=request.form['publication_year'],
            category=request.form['category'],
            description=request.form['description']
        )
        book.save()
        flash('Book successfully created!')
        return redirect(url_for('books.list'))
    
    return render_template('books/create.html')

@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@admin_required
def edit(id):
    book = Book.get_by_id(id)
    if request.method == 'POST':
        book = Book(
            id=id,
            title=request.form['title'],
            author=request.form['author'],
            isbn=request.form['isbn'],
            publisher=request.form['publisher'],
            publication_year=request.form['publication_year'],
            category=request.form['category'],
            description=request.form['description']
        )
        book.save()
        flash('Book successfully updated!')
        return redirect(url_for('books.list'))
    
    return render_template('books/edit.html', book=book)

@bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete(id):
    Book.delete(id)
    flash('Book successfully deleted!')
    return redirect(url_for('books.list'))

@bp.route('/<int:id>')
@login_required
def detail(id):
    book = Book.get_by_id(id)
    reviews = Review.get_by_book_id(id)
    user_review = None
    if 'user_id' in session:
        user_review = Review.get_user_review(id, session['user_id'])
        if user_review:
            for review in reviews:
                review['user_liked'] = ReviewLike.get_user_like(review['review_id'], session['user_id'])
                cur = mysql.connection.cursor()
                cur.execute('''
                    SELECT 1 FROM review_reports 
                    WHERE review_id = %s AND reporter_id = %s
                ''', (review['review_id'], session['user_id']))
                review['is_reported'] = bool(cur.fetchone())
                cur.close()
            
    return render_template('books/detail.html', 
                         book=book, 
                         reviews=reviews, 
                         user_review=user_review)

@bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('books.list'))
    
    books = Book.search(query)
    return render_template('books/search.html', books=books, query=query) 