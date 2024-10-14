from flask import render_template, request, redirect, url_for, jsonify, flash, abort
from app import app, db
from models import Sponsor, User
from datetime import datetime, timedelta
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError, DataError
from app import check_upcoming_sponsors
from email_utils import send_sponsor_notification, send_superuser_invitation, send_otp
import smtplib
import logging
from sqlalchemy import func
from functools import wraps
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
def search_sponsors():
    query = request.args.get('query', '')
    sponsors = Sponsor.query.filter(
        Sponsor.name.ilike(f'%{query}%') |
        Sponsor.email.ilike(f'%{query}%') |
        Sponsor.phone.ilike(f'%{query}%')
    ).all()
    return jsonify([sponsor.to_dict() for sponsor in sponsors])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        try:
            # Check if this is the first user
            is_first_user = User.query.count() == 0
            new_user = User(username=username, email=email, password_hash=generate_password_hash(password), is_superuser=is_first_user)
            db.session.add(new_user)
            db.session.commit()
            
            if is_first_user:
                new_user.is_verified = True
                db.session.commit()
                flash('You have been registered as the first superuser. Please log in.', 'success')
            else:
                flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Username or email already exists. Please choose a different one.', 'danger')
        except DataError:
            db.session.rollback()
            flash('An error occurred while processing your registration. Please try again.', 'danger')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Error during registration: {str(e)}')
            flash('An unexpected error occurred. Please try again later.', 'danger')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            if user.is_superuser and not user.is_verified:
                # Generate and send OTP
                otp = secrets.randbelow(1000000)
                user.otp = f"{otp:06d}"
                db.session.commit()
                send_otp(user.email, user.otp)
                return redirect(url_for('verify_otp', user_id=user.id))
            login_user(user)
            logger.info(f"User {user.username} logged in. Superuser: {user.is_superuser}")
            if user.is_admin():
                flash('Logged in as superuser.', 'success')
            else:
                flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/verify_otp/<int:user_id>', methods=['GET', 'POST'])
def verify_otp(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        otp = request.form['otp']
        if otp == user.otp:
            user.is_verified = True
            user.otp = None
            db.session.commit()
            login_user(user)
            flash('OTP verified successfully. You are now logged in as a superuser.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
    return render_template('verify_otp.html', user_id=user_id)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized"}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({"error": "Forbidden"}), 403

@app.route('/create_test_sponsor')
@login_required
@superuser_required
def create_test_sponsor():
    try:
        test_sponsor = Sponsor(
            name="Test Sponsor",
            phone="1234567890",
            email="test@example.com",
            date=datetime.now().date() + timedelta(days=1)
        )
        db.session.add(test_sponsor)
        db.session.commit()
        
        logger.info(f"Test sponsor created: {test_sponsor.name}, ID: {test_sponsor.id}")
        
        try:
            send_sponsor_notification(test_sponsor)
            flash('Test sponsor created and email notification sent successfully.', 'success')
            logger.info('Email notification sent successfully for test sponsor.')
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f'Test sponsor created, but email notification failed due to authentication error: {str(e)}'
            flash(error_msg, 'warning')
            logger.error(error_msg)
        except Exception as e:
            error_msg = f'Test sponsor created, but email notification failed: {str(e)}'
            flash(error_msg, 'warning')
            logger.error(error_msg)
        
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        error_msg = f'Error creating test sponsor: {str(e)}'
        flash(error_msg, 'danger')
        logger.error(error_msg)
        return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    total_sponsors = Sponsor.query.count()
    upcoming_sponsors = Sponsor.query.filter(Sponsor.date >= datetime.now().date()).count()
    
    sponsors_by_month = db.session.query(
        func.extract('month', Sponsor.date).label('month'),
        func.count(Sponsor.id).label('count')
    ).group_by('month').order_by('month').all()

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    sponsor_counts = [0] * 12
    for month, count in sponsors_by_month:
        sponsor_counts[int(month) - 1] = count

    top_upcoming_sponsors = Sponsor.query.filter(Sponsor.date >= datetime.now().date()).order_by(Sponsor.date).limit(5).all()

    return render_template('dashboard.html', 
                           total_sponsors=total_sponsors, 
                           upcoming_sponsors=upcoming_sponsors,
                           months=months,
                           sponsor_counts=sponsor_counts,
                           top_upcoming_sponsors=top_upcoming_sponsors)

@app.route('/admin')
@login_required
@superuser_required
def admin():
    logger.info(f"Superuser {current_user.username} accessed admin panel")
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/admin/toggle_superuser/<int:user_id>', methods=['POST'])
@login_required
@superuser_required
def toggle_superuser(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('You cannot change your own superuser status.', 'danger')
    else:
        user.is_superuser = not user.is_superuser
        if user.is_superuser:
            user.is_verified = False
        db.session.commit()
        flash(f'Superuser status for {user.username} has been updated.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/invite_superuser', methods=['GET', 'POST'])
@login_required
@superuser_required
def invite_superuser():
    if request.method == 'POST':
        email = request.form['email']
        if User.query.filter_by(email=email).first():
            flash('A user with this email already exists.', 'danger')
        else:
            token = secrets.token_urlsafe(32)
            send_superuser_invitation(email, token)
            flash(f'Invitation sent to {email}', 'success')
        return redirect(url_for('admin'))
    return render_template('invite_superuser.html')

@app.route('/register_superuser/<token>', methods=['GET', 'POST'])
def register_superuser(token):
    # In a real application, you would validate the token here
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        try:
            new_user = User(username=username, email=email, password_hash=generate_password_hash(password), is_superuser=True)
            db.session.add(new_user)
            db.session.commit()
            flash('You have been registered as a superuser. Please log in to verify your account.', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Username or email already exists. Please choose a different one.', 'danger')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Error during superuser registration: {str(e)}')
            flash('An unexpected error occurred. Please try again later.', 'danger')
    
    return render_template('register_superuser.html', token=token)
