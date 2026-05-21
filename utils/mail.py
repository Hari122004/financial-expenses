import os
import smtplib
from email.message import EmailMessage
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_smtp_settings():
    return {
        "host": os.getenv("SMTP_HOST", ""),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "username": os.getenv("SMTP_USERNAME", ""),
        "password": os.getenv("SMTP_PASSWORD", ""),
        "from_email": os.getenv("SMTP_FROM", os.getenv("SMTP_USERNAME", "")),
        "use_tls": os.getenv("SMTP_USE_TLS", "True").lower() in ("true", "1", "yes", "y")
    }


def validate_smtp_settings(settings):
    missing = [
        key for key in ["host", "username", "password", "from_email"]
        if not settings.get(key)
    ]

    if missing:
        raise ValueError(
            "SMTP settings are missing: " + ", ".join(missing) + ". "
            "Set SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, and SMTP_FROM."
        )

    return settings


def send_email(subject, body, to_email, html=False):
    settings = validate_smtp_settings(get_smtp_settings())

    try:
        logger.debug(f"Preparing email to {to_email}")
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = settings["from_email"]
        message["To"] = to_email

        if html:
            message.add_alternative(body, subtype="html")
        else:
            message.set_content(body)

        logger.debug(f"Connecting to {settings['host']}:{settings['port']}")
        with smtplib.SMTP(settings["host"], settings["port"], timeout=10) as smtp:
            if settings["use_tls"]:
                logger.debug("Starting TLS")
                smtp.starttls()
            logger.debug(f"Logging in as {settings['username']}")
            smtp.login(settings["username"], settings["password"])
            logger.debug(f"Sending email to {to_email}")
            smtp.send_message(message)
            logger.info(f"Email sent successfully to {to_email}")
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed: {e}")
        raise Exception(f"Email authentication failed. Check your Gmail app password.") from e
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        raise Exception(f"SMTP error occurred: {e}") from e
    except Exception as e:
        logger.error(f"Email sending failed: {type(e).__name__}: {e}")
        raise


def send_welcome_email(to_email, username):
    subject = "Welcome to Expense Tracker"
    body = f"""
Hello {username},

Welcome to Expense Tracker!

Your account is ready and you can now start tracking your expenses, budgets, and spending habits.

If you have any questions, just reply to this email.

Best,
The Expense Tracker Team
"""
    send_email(subject, body, to_email)
