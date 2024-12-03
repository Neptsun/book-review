from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        error = None
        
        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif User.get_by_email(email) is not None:
            error = f'Email {email} is already registered.'
            
        if error is None:
            user = User(username=username, email=email, password=password)
            user.save()
            flash('Registration successful! Please log in.')
            return redirect(url_for('auth.login'))
            
        flash(error)
        
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        error = None
        user = User.get_by_email(email)
        
        if user is None:
            error = 'Incorrect email.'
        elif not User.verify_password(user['password_hash'], password):
            error = 'Incorrect password.'
            
        if error is None:
            session.clear()
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['is_admin'] = user['role'] == 'admin'
            return redirect(url_for('index'))
            
        flash(error)
        
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('auth.login')) 