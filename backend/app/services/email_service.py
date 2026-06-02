import logging
import smtplib
from email.mime.text import MIMEText

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def send_email(subject: str, recipient: str, body: str) -> bool:
    """Send email when SMTP is configured. Returns True on success, False on skip/failure."""
    settings = get_settings()
    if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password:
        return False

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = settings.smtp_from
    message["To"] = recipient

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from, [recipient], message.as_string())
        return True
    except smtplib.SMTPException as exc:
        logger.warning("SMTP send failed for %s: %s", recipient, exc)
        return False
    except OSError as exc:
        logger.warning("SMTP connection failed: %s", exc)
        return False
