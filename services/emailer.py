import smtplib
from email.message import EmailMessage

from flask import current_app


def email_configured():
    config = current_app.config
    return bool(config.get("MAIL_SERVER") and config.get("MAIL_DEFAULT_SENDER"))


def send_email(to_email, subject, body):
    config = current_app.config
    server = config.get("MAIL_SERVER")
    sender = config.get("MAIL_DEFAULT_SENDER")
    username = config.get("MAIL_USERNAME")
    password = config.get("MAIL_PASSWORD")
    if not email_configured():
        return False, "Email is not configured."

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = to_email
    message.set_content(body)

    try:
        with smtplib.SMTP(server, config.get("MAIL_PORT", 587), timeout=15) as smtp:
            if config.get("MAIL_USE_TLS", True):
                smtp.starttls()
            if username and password:
                smtp.login(username, password)
            smtp.send_message(message)
    except OSError as error:
        return False, f"Email failed: {error}"
    except smtplib.SMTPException as error:
        return False, f"Email failed: {error}"
    return True, "Email sent."
