from flask_mail import Message
from app import mail, app
from flask import render_template, url_for
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

def send_superuser_invitation(email, token):
    subject = "Invitation to become a Superuser"
    recipients = [email]
    
    invitation_link = url_for('register_superuser', token=token, _external=True)
    
    msg = Message(subject=subject, recipients=recipients)
    msg.body = f"You have been invited to become a superuser. Please click the following link to register: {invitation_link}"
    msg.html = render_template('email/superuser_invitation.html', invitation_link=invitation_link)
    
    try:
        mail.send(msg)
        logger.info(f"Superuser invitation sent successfully to: {email}")
    except Exception as e:
        logger.error(f"Error sending superuser invitation: {str(e)}")
        raise

def send_otp(email, otp):
    subject = "OTP for Superuser Verification"
    recipients = [email]
    
    msg = Message(subject=subject, recipients=recipients)
    msg.body = f"Your OTP for superuser verification is: {otp}"
    msg.html = render_template('email/otp_verification.html', otp=otp)
    
    try:
        mail.send(msg)
        logger.info(f"OTP sent successfully to: {email}")
    except Exception as e:
        logger.error(f"Error sending OTP: {str(e)}")
        raise

def send_superuser_upgrade_confirmation(email):
    subject = "Superuser Status Upgrade Confirmation"
    recipients = [email]
    
    msg = Message(subject=subject, recipients=recipients)
    msg.body = "Your account has been upgraded to superuser status. Please log in to verify your account."
    msg.html = render_template('email/superuser_upgrade_confirmation.html')
    
    try:
        mail.send(msg)
        logger.info(f"Superuser upgrade confirmation sent successfully to: {email}")
    except Exception as e:
        logger.error(f"Error sending superuser upgrade confirmation: {str(e)}")
        raise
