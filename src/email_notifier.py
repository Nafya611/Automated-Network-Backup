"""
Email Notifier for Network Device Backup Tool

Handles sending email notifications on backup success/failure.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List

class EmailNotifier:
    """Handles email notifications for backup events."""
    def __init__(self, email_config: dict):
        self.enabled = email_config.get('enabled', False)
        self.smtp_server = email_config.get('smtp_server', '')
        self.smtp_port = email_config.get('smtp_port', 587)
        self.sender_email = email_config.get('sender_email', '')
        self.sender_password = email_config.get('sender_password', '')
        self.recipient_email = email_config.get('recipient_email', '')
        self.logger = logging.getLogger(__name__)

    def send_notification(self, subject: str, body: str) -> bool:
        if not self.enabled:
            self.logger.info("Email notifications are disabled.")
            return False
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            self.logger.info(f"Email sent: {subject}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False

    def send_backup_report(self, success_count: int, fail_count: int, errors: List[str]):
        subject = f"Network Backup Report: {success_count} Success, {fail_count} Failed"
        body = f"Backup completed.\n\nSuccess: {success_count}\nFailed: {fail_count}\n"
        if errors:
            body += "\nErrors:\n" + "\n".join(errors)
        self.send_notification(subject, body)
