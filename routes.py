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

    return jsonify([sponsor.to_dict() for sponsor in sponsors])

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

# ... [rest of the code remains unchanged]
