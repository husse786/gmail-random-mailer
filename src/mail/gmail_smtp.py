

from __future__ import annotations

import smtplib
from email.message import EmailMessage

from src.ai.generator import EmailContent
from src.config.settings import Settings


SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def build_message(
    *,
    from_email: str,
    to_email: str,
    content: EmailContent,
) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = content.subject

    # Plain text body
    msg.set_content(content.body)
    return msg


def send_email(
    settings: Settings,
    *,
    to_email: str,
    content: EmailContent,
) -> None:
    """Sendet eine E-Mail via Gmail SMTP (STARTTLS)."""

    msg = build_message(
        from_email=settings.gmail_address,
        to_email=to_email,
        content=content,
    )

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(settings.gmail_address, settings.gmail_app_password)
        server.send_message(msg)