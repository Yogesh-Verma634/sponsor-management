from flask import render_template, request, redirect, url_for, jsonify
from app import app, db
from models import Sponsor
from datetime import datetime

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_sponsor', methods=['POST'])
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
def get_sponsors():
    start_date = request.args.get('start')
    end_date = request.args.get('end')

    sponsors = Sponsor.query.filter(
        Sponsor.date >= start_date,
        Sponsor.date <= end_date
    ).all()

    return jsonify([sponsor.to_dict() for sponsor in sponsors])
