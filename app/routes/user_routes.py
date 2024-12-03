from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.models.user import User
from app.auth import login_required

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/profile')
@login_required
def profile():
    user = User.get_by_id(session['user_id'])
    if not user:
        flash('User not found.')
        return redirect(url_for('index'))
    
    stats = User.get_user_stats(user['user_id'])
    reviews = User.get_user_reviews(user['user_id'])
    
    return render_template('users/profile.html', 
                         user=user, 
                         stats=stats, 
                         reviews=reviews) 