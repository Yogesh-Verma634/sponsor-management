from flask_mail import Message
from app import mail, app
from flask import render_template
import smtplib
import logging

logger = logging.getLogger(__name__)

def send_sponsor_notification(sponsor):
    subject = f"Upcoming Sponsor: {sponsor.name}"
    recipients = [app.config['MAIL_DEFAULT_SENDER']]  # Send to temple management
    
    msg = Message(subject=subject, recipients=recipients)
    msg.body = render_template('email/sponsor_notification.txt', sponsor=sponsor)
    msg.html = render_template('email/sponsor_notification.html', sponsor=sponsor)
    
    try:
        logger.info(f"Attempting to send email notification for sponsor: {sponsor.name}")
        logger.info(f"SMTP Server: {app.config['MAIL_SERVER']}")
        logger.info(f"SMTP Port: {app.config['MAIL_PORT']}")
        logger.info(f"TLS Enabled: {app.config['MAIL_USE_TLS']}")
        logger.info(f"Sender: {app.config['MAIL_DEFAULT_SENDER']}")
        
        mail.send(msg)
        logger.info(f"Email notification sent successfully for sponsor: {sponsor.name}")
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication Error: {str(e)}")
        logger.error(f"Please check your MAIL_USERNAME and MAIL_PASSWORD environment variables.")
        logger.error("If using Gmail, ensure 'Less secure app access' is enabled or use an app-specific password.")
        raise
    except Exception as e:
        logger.error(f"Error sending email notification: {str(e)}")
        raise
