from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.review import Review
from app.models.book import Book
from app.auth import login_required

bp = Blueprint('reviews', __name__, url_prefix='/reviews')

@bp.route('/book/<int:book_id>/add', methods=['POST'])
@login_required
def add(book_id):
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment')
    
    if not rating or rating < 1 or rating > 5:
        flash('Rating must be between 1 and 5.')
        return redirect(url_for('books.detail', id=book_id))
        
    # Check if user already reviewed this book
    existing_review = Review.get_user_review(book_id, session['user_id'])
    if existing_review:
        flash('You have already reviewed this book.')
        return redirect(url_for('books.detail', id=book_id))
    
    review = Review(
        book_id=book_id,
        user_id=session['user_id'],
        rating=rating,
        comment=comment
    )
    review.save()
    
    flash('Your review has been added.')
    return redirect(url_for('books.detail', id=book_id))

@bp.route('/<int:id>/edit', methods=['POST'])
@login_required
def edit(id):
    review = Review.get_by_id(id)
    if not review or review['user_id'] != session['user_id']:
        flash('Review not found or unauthorized.')
        return redirect(url_for('books.list'))
    
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment')
    
    if not rating or rating < 1 or rating > 5:
        flash('Rating must be between 1 and 5.')
        return redirect(url_for('books.detail', id=review['book_id']))
    
    updated_review = Review(
        id=id,
        book_id=review['book_id'],
        user_id=session['user_id'],
        rating=rating,
        comment=comment
    )
    updated_review.save()
    
    flash('Your review has been updated.')
    return redirect(url_for('books.detail', id=review['book_id']))

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    review = Review.get_by_id(id)
    if not review or review['user_id'] != session['user_id']:
        flash('Review not found or unauthorized.')
        return redirect(url_for('books.list'))
    
    if Review.delete(id):
        flash('Your review has been deleted.')
    else:
        flash('Failed to delete review.')
    return redirect(url_for('books.detail', id=review['book_id'])) 