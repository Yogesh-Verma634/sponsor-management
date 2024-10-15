from flask import render_template, request, redirect, url_for, jsonify, flash, abort
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy import func
from functools import wraps
from datetime import datetime, timedelta
from app import app, db, check_upcoming_sponsors
from models import Sponsor, User
from email_utils import send_sponsor_notification, send_superuser_invitation, send_otp, send_superuser_upgrade_confirmation
import smtplib
import logging
import secrets

logger = logging.getLogger(__name__)

def superuser_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            logger.warning(f"Unauthenticated user attempted to access {f.__name__}")
            return redirect(url_for('login', next=request.url))
        if not current_user.is_admin():
            logger.warning(f"Non-superuser {current_user.username} attempted to access {f.__name__}")
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        logger.info(f"Superuser {current_user.username} accessed {f.__name__}")
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
@superuser_required
def dashboard():
    total_users = User.query.count()
    total_sponsors = Sponsor.query.count()
    recent_sponsors = Sponsor.query.order_by(Sponsor.created_at.desc()).limit(5).all()
    return render_template('dashboard.html', total_users=total_users, total_sponsors=total_sponsors, recent_sponsors=recent_sponsors)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        try:
            db.session.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Username or email already exists.', 'danger')
    return render_template('register.html')

@app.route('/add_sponsor', methods=['POST'])
@login_required
@superuser_required
def add_sponsor():
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()

    new_sponsor = Sponsor(name=name, phone=phone, email=email, date=date)
    db.session.add(new_sponsor)
    db.session.commit()

    flash('Sponsor added successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/get_sponsors', methods=['GET'])
@login_required
def get_sponsors():
    start_date = request.args.get('start')
    end_date = request.args.get('end')

    sponsors = Sponsor.query.filter(
        Sponsor.date >= start_date,
        Sponsor.date <= end_date
    ).all()

    if current_user.is_admin():
        return jsonify([sponsor.to_dict() for sponsor in sponsors])
    else:
        return jsonify([{
            'id': sponsor.id,
            'name': sponsor.name,
            'date': sponsor.date.isoformat()
        } for sponsor in sponsors])

@app.route('/search_sponsors', methods=['GET'])
@login_required
@superuser_required
def search_sponsors():
    query = request.args.get('query', '')
    sponsors = Sponsor.query.filter(
        Sponsor.name.ilike(f'%{query}%') |
        Sponsor.email.ilike(f'%{query}%') |
        Sponsor.phone.ilike(f'%{query}%')
    ).all()
    
    return jsonify([sponsor.to_dict() for sponsor in sponsors])

@app.route('/admin')
@login_required
@superuser_required
def admin():
    users = User.query.all()
    return render_template('admin.html', users=users)

# ... [rest of the code remains unchanged]
