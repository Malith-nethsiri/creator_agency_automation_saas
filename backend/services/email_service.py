import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAILS_FROM_EMAIL = os.getenv("EMAILS_FROM_EMAIL")
EMAILS_FROM_NAME = os.getenv("EMAILS_FROM_NAME", "Creator Agency SaaS")


class EmailService:
    @staticmethod
    def send_email(to_email: str, subject: str, body: str, html: Optional[str] = None):
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{EMAILS_FROM_NAME} <{EMAILS_FROM_EMAIL}>"
            msg["To"] = to_email
            msg["Subject"] = subject

            # Plain text fallback
            msg.attach(MIMEText(body, "plain"))

            # HTML version if provided
            if html:
                msg.attach(MIMEText(html, "html"))

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(EMAILS_FROM_EMAIL, to_email, msg.as_string())

            print(f"✅ Email sent to {to_email}")

        except Exception as e:
            print(f"❌ Email sending failed: {str(e)}")


email_service = EmailService()
