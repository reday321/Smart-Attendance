from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from ..models.user import User
from .. import db
from sqlalchemy.exc import IntegrityError

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            # Clear any existing messages before redirecting
            session.pop('_flashes', None)
            return redirect(url_for('main.index'))
        flash('Invalid username or password', 'danger')
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        department = request.form.get('department')
        role = request.form.get('role', 'student')

        # Check for existing username
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))

        # Check for existing email
        if User.query.filter_by(email=email).first():
            flash('Email address already registered', 'danger')
            return redirect(url_for('auth.register'))

        try:
            user = User(username=username, email=email, department=department, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except IntegrityError:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('auth.register'))
        except Exception as e:
            db.session.rollback()
            flash('An unexpected error occurred. Please try again.', 'danger')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        department = request.form.get('department')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Check if username is taken by another user
        user_check = User.query.filter(User.username == username, User.id != current_user.id).first()
        if user_check:
            flash('Username already taken', 'danger')
            return redirect(url_for('auth.profile'))

        # Check if email is taken by another user
        email_check = User.query.filter(User.email == email, User.id != current_user.id).first()
        if email_check:
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.profile'))

        # Update basic info
        current_user.username = username
        current_user.email = email
        current_user.department = department

        # Handle password change if requested
        if current_password and new_password:
            if not current_user.check_password(current_password):
                flash('Current password is incorrect', 'danger')
                return redirect(url_for('auth.profile'))
            
            if new_password != confirm_password:
                flash('New passwords do not match', 'danger')
                return redirect(url_for('auth.profile'))
            
            current_user.set_password(new_password)
            flash('Password updated successfully', 'success')

        try:
            db.session.commit()
            flash('Profile updated successfully', 'success')
        except:
            db.session.rollback()
            flash('An error occurred while updating profile', 'danger')

        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')