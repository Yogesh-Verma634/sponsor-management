from flask import render_template, request, redirect, url_for, jsonify, flash
from app import app, db
from models import Sponsor, User
from datetime import datetime, timedelta
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError, DataError
from app import check_upcoming_sponsors

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/add_sponsor', methods=['POST'])
@login_required
def add_sponsor():
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()

    new_sponsor = Sponsor(name=name, phone=phone, email=email, date=date)
    db.session.add(new_sponsor)
    db.session.commit()

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        try:
            new_user = User(username=username, email=email, password_hash=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
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
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized"}), 401

@app.route('/create_test_sponsor')
@login_required
def create_test_sponsor():
    test_sponsor = Sponsor(
        name="Test Sponsor",
        phone="1234567890",
        email="test@example.com",
        date=datetime.now().date() + timedelta(days=1)
    )
    db.session.add(test_sponsor)
    db.session.commit()
    
    # Manually trigger the check_upcoming_sponsors function
    check_upcoming_sponsors()
    
    flash('Test sponsor created and email notification sent.', 'success')
    return redirect(url_for('index'))
