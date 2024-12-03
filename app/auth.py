from functools import wraps
from flask import session, redirect, url_for, flash
from app.models.user import User

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash('Please log in first.')
            return redirect(url_for('auth.login'))
            
        return view(**kwargs)
        
    return wrapped_view

def admin_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash('Please log in first.')
            return redirect(url_for('auth.login'))
            
        user = User.get_by_id(session['user_id'])
        if user['role'] != 'admin':
            flash('Admin access required.')
            return redirect(url_for('books.list'))
            
        return view(**kwargs)
        
    return wrapped_view 