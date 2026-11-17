# backend/services/mail.py
# by LECHAT Jérôme; creation date: 09/2025, last edit: 11/2026

# INTERNAL(S)
import json
import logging
import mimetypes
import smtplib
from email.message import EmailMessage
from pathlib import Path

# MODULE(S)
from backend.services.user_service import UserService

LOG = logging.getLogger(__name__)


class MailService:
    """
    Service responsible for constructing and sending emails via SMTP (SSL).
    Supports plain text, HTML formats, and dynamic MIME-type attachments.
    """

    def __init__(self, sender_email: str, password: str, smtp_server: str = "smtp.gmail.com", smtp_port: int = 465, config: UserService | None = None) -> None:
        """
        Initializes the mail sending service.

        Args:
            sender_email (str): The sender's email address.
            password (str): The email account password or app-specific password (recommended for Gmail).
            smtp_server (str): SMTP server address (default: Gmail).
            smtp_port (int): SMTP port (default: 465 for SSL).
            config (UserService | None): Optional user configuration.
        """

        # === variable(s) ===
        self.sender_email = sender_email
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

        self.user_config = config

    def __str__(self) -> str:
        return f"[MailService]: using account {self.sender_email}."


    # === Public Method(s) ===
    def send_email(self, recipient: str | list[str], subject: str, body: str, attachments: list[str | Path] | None = None, html: bool = False) -> None:
        """
        Sends an email via SMTP (SSL).

        Args:
            recipient (str | list[str]): Recipient(s) email address(es).
            subject (str): Email subject.
            body (str): Email body content.
            attachments (list[str | Path] | None): List of file paths to attach.
            html (bool): Whether to send the body as HTML.

        Raises:
            Exception: If the SMTP connection fails, login is rejected, or message cannot be sent.
        """
        email = self._create_message(recipient, subject, body, attachments, html)

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as smtp:
                smtp.login(self.sender_email, self.password)
                smtp.send_message(email)
        except Exception as e:
            LOG.error(f"Failed to send email via {self.smtp_server}:{self.smtp_port}: {e}")
            raise


    # === Private Method(s) ===
    def _create_message(self, recipient: str | list[str], subject: str, body: str, attachments: list[str | Path] | None = None, html: bool = False) -> EmailMessage:
        """
        Builds an EmailMessage object ready to be sent.

        Args:
            recipients (str | list[str]): Recipient(s) email address(es).
            subject (str): Email subject.
            body (str): Email body (plain text or HTML).
            attachments (list[str] | None): List of file paths to attach.
            html (bool): Whether to send the body as HTML.

        Returns:
            EmailMessage: The prepared email message.
        """
        message = EmailMessage()

        # e-mail setup ('Subject', 'From', 'To')
        message["Subject"] = subject
        message["From"] = self.sender_email
        message["To"] = recipient if isinstance(recipient, str) else ", ".join(recipient)

        if html:
            message.add_alternative(body, subtype="html")
        else:
            message.set_content(body)

        # e-mail setup ('Attachments')
        if attachments:
            for filepath in attachments:
                path = Path(filepath)
                if not path.exists():
                    LOG.warning(f"Attachment not found, skipping: {path}.")
                    continue

                # dynamic detection using MIME
                ctype, encoding = mimetypes.guess_type(path)
                if ctype is None or encoding is not None:
                    ctype = "application/octet-stream"

                maintype, subtype = ctype.split("/", 1)

                with open(path, "rb") as f:
                    message.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=path.name)

        return message
