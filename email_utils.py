from flask_mail import Message
from app import mail, app
from flask import render_template
import smtplib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_sponsor_notification(sponsor):
    subject = f"Upcoming Sponsor: {sponsor.name}"
    recipients = [app.config['MAIL_DEFAULT_SENDER']]  # Send to temple management
    
    msg = Message(subject=subject, recipients=recipients)
    msg.body = render_template('email/sponsor_notification.txt', sponsor=sponsor)
    msg.html = render_template('email/sponsor_notification.html', sponsor=sponsor)
    
    try:
        mail.send(msg)
        logger.info(f"Email notification sent for sponsor: {sponsor.name}")
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication Error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error sending email notification: {str(e)}")
        raise
