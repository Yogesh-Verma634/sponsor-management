from flask_mail import Message
from app import mail, app
from flask import render_template

def send_sponsor_notification(sponsor):
    subject = f"Upcoming Sponsor: {sponsor.name}"
    recipients = [app.config['MAIL_DEFAULT_SENDER']]  # Send to temple management
    
    msg = Message(subject=subject, recipients=recipients)
    msg.body = render_template('email/sponsor_notification.txt', sponsor=sponsor)
    msg.html = render_template('email/sponsor_notification.html', sponsor=sponsor)
    
    mail.send(msg)
