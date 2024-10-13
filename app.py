import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()
scheduler = BackgroundScheduler()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

db.init_app(app)
login_manager.init_app(app)
migrate.init_app(app, db)
mail.init_app(app)
login_manager.login_view = 'login'

with app.app_context():
    import models
    from email_utils import send_sponsor_notification

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))

def check_upcoming_sponsors():
    with app.app_context():
        today = datetime.now().date()
        upcoming_date = today + timedelta(days=7)  # Check for sponsors in the next 7 days
        upcoming_sponsors = models.Sponsor.query.filter(
            models.Sponsor.date >= today,
            models.Sponsor.date <= upcoming_date
        ).all()

        for sponsor in upcoming_sponsors:
            send_sponsor_notification(sponsor)

scheduler.add_job(func=check_upcoming_sponsors, trigger="interval", hours=24)
scheduler.start()

import routes

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
