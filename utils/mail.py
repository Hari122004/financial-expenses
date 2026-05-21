import os
import smtplib
from email.message import EmailMessage


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

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings["from_email"]
    message["To"] = to_email

    if html:
        message.add_alternative(body, subtype="html")
    else:
        message.set_content(body)

    with smtplib.SMTP(settings["host"], settings["port"]) as smtp:
        if settings["use_tls"]:
            smtp.starttls()
        smtp.login(settings["username"], settings["password"])
        smtp.send_message(message)


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
