from app import db
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import func

class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, phone, email, date):
        self.name = name
        self.phone = phone
        self.email = email
        self.date = date

    def __repr__(self):
        return f'<Sponsor {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'date': self.date.isoformat(),
        }

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512))
    is_superuser = db.Column(db.Boolean, default=False)
    otp = db.Column(db.String(6))
    is_verified = db.Column(db.Boolean, default=False)
    # is_active = db.Column(db.Boolean, default=True)

    def __init__(self, username, email, password_hash, is_superuser=False):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_superuser = is_superuser
        # self.is_active = True

    def __repr__(self):
        return f'<User {self.username}>'

    def is_admin(self):
        return self.is_superuser and self.is_verified

    @classmethod
    def is_first_user(cls):
        return cls.query.count() == 0
