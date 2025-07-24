import smtplib
import ssl
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import List, Optional
from datetime import datetime, timedelta
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_tls = settings.SMTP_TLS
        self.from_email = settings.EMAIL_FROM or settings.SMTP_USER
        self.from_name = settings.EMAIL_FROM_NAME

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email using SMTP configuration"""
        try:
            # Create message
            message = MimeMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            # Add text content if provided
            if text_content:
                text_part = MimeText(text_content, "plain")
                message.attach(text_part)

            # Add HTML content
            html_part = MimeText(html_content, "html")
            message.attach(html_part)

            # Create SMTP session
            if self.smtp_tls:
                context = ssl.create_default_context()
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls(context=context)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)

            # Login and send email
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.from_email, to_email, message.as_string())
            server.quit()

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def send_welcome_email(self, user_email: str, user_name: str = None) -> bool:
        """Send welcome email to new user"""
        subject = f"Welcome to {settings.PROJECT_NAME}!"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to {settings.PROJECT_NAME}!</h1>
                </div>
                <div class="content">
                    <h2>Hello {user_name or 'there'}! 👋</h2>
                    <p>Thank you for joining our platform! We're excited to have you on board.</p>

                    <p>With {settings.PROJECT_NAME}, you can:</p>
                    <ul>
                        <li>🎨 Upload and manage your creative content</li>
                        <li>📊 Generate detailed reports</li>
                        <li>💼 Connect with agencies and creators</li>
                        <li>🚀 Scale your creative business</li>
                    </ul>

                    <p>Ready to get started?</p>
                    <a href="{settings.STRIPE_SUCCESS_URL.replace('/success', '/dashboard')}" class="button">Go to Dashboard</a>

                    <p>If you have any questions, feel free to reach out to our support team.</p>

                    <p>Best regards,<br>The {settings.PROJECT_NAME} Team</p>
                </div>
                <div class="footer">
                    <p>© 2024 {settings.PROJECT_NAME}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Welcome to {settings.PROJECT_NAME}!

        Hello {user_name or 'there'}!

        Thank you for joining our platform! We're excited to have you on board.

        With {settings.PROJECT_NAME}, you can:
        - Upload and manage your creative content
        - Generate detailed reports
        - Connect with agencies and creators
        - Scale your creative business

        Best regards,
        The {settings.PROJECT_NAME} Team
        """

        return self.send_email(user_email, subject, html_content, text_content)

    def send_subscription_success_email(
        self,
        user_email: str,
        user_name: str,
        plan_name: str,
        plan_price: float,
        billing_period_end: Optional[datetime] = None
    ) -> bool:
        """Send subscription success email"""
        subject = f"Subscription Activated - {plan_name}"

        # Calculate billing period end if not provided (assume monthly)
        if not billing_period_end:
            billing_period_end = datetime.now() + timedelta(days=30)

        formatted_date = billing_period_end.strftime("%B %d, %Y")

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .plan-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745; }}
                .button {{ display: inline-block; background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Subscription Activated!</h1>
                </div>
                <div class="content">
                    <h2>Hello {user_name}!</h2>
                    <p>Great news! Your subscription has been successfully activated.</p>

                    <div class="plan-details">
                        <h3>📋 Subscription Details</h3>
                        <p><strong>Plan:</strong> {plan_name}</p>
                        <p><strong>Price:</strong> ${plan_price:.2f}/month</p>
                        <p><strong>Next billing date:</strong> {formatted_date}</p>
                        <p><strong>Status:</strong> Active ✅</p>
                    </div>

                    <p>You now have full access to all {plan_name} features. Start exploring and make the most of your subscription!</p>

                    <a href="{settings.STRIPE_SUCCESS_URL.replace('/success', '/dashboard')}" class="button">Access Dashboard</a>

                    <p>Questions about your subscription? Contact our support team anytime.</p>

                    <p>Thank you for choosing {settings.PROJECT_NAME}!</p>

                    <p>Best regards,<br>The {settings.PROJECT_NAME} Team</p>
                </div>
                <div class="footer">
                    <p>© 2024 {settings.PROJECT_NAME}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Subscription Activated!

        Hello {user_name}!

        Great news! Your subscription has been successfully activated.

        Subscription Details:
        - Plan: {plan_name}
        - Price: ${plan_price:.2f}/month
        - Next billing date: {formatted_date}
        - Status: Active

        You now have full access to all {plan_name} features.

        Thank you for choosing {settings.PROJECT_NAME}!

        Best regards,
        The {settings.PROJECT_NAME} Team
        """

        return self.send_email(user_email, subject, html_content, text_content)

    def send_subscription_cancellation_email(
        self,
        user_email: str,
        user_name: str,
        plan_name: str,
        cancellation_date: Optional[datetime] = None
    ) -> bool:
        """Send subscription cancellation email"""
        subject = f"Subscription Cancelled - {plan_name}"

        if not cancellation_date:
            cancellation_date = datetime.now()

        formatted_date = cancellation_date.strftime("%B %d, %Y")

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .cancellation-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #dc3545; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Subscription Cancelled</h1>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>We're sorry to see you go! Your subscription has been successfully cancelled.</p>

                    <div class="cancellation-details">
                        <h3>📋 Cancellation Details</h3>
                        <p><strong>Plan:</strong> {plan_name}</p>
                        <p><strong>Cancellation date:</strong> {formatted_date}</p>
                        <p><strong>Status:</strong> Cancelled ❌</p>
                    </div>

                    <p>Your access will continue until the end of your current billing period. After that, your account will be downgraded to our free tier.</p>

                    <p><strong>What happens next?</strong></p>
                    <ul>
                        <li>No further charges will be made</li>
                        <li>You can still access your content until the billing period ends</li>
                        <li>Your data will be safely stored</li>
                        <li>You can reactivate anytime</li>
                    </ul>

                    <p>We'd love to have you back! If you change your mind, you can resubscribe anytime.</p>

                    <a href="{settings.STRIPE_SUCCESS_URL.replace('/success', '/plans')}" class="button">View Plans</a>

                    <p>If you cancelled by mistake or need help, please contact our support team.</p>

                    <p>Thank you for being part of {settings.PROJECT_NAME}!</p>

                    <p>Best regards,<br>The {settings.PROJECT_NAME} Team</p>
                </div>
                <div class="footer">
                    <p>© 2024 {settings.PROJECT_NAME}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Subscription Cancelled

        Hello {user_name},

        We're sorry to see you go! Your subscription has been successfully cancelled.

        Cancellation Details:
        - Plan: {plan_name}
        - Cancellation date: {formatted_date}
        - Status: Cancelled

        Your access will continue until the end of your current billing period.

        What happens next?
        - No further charges will be made
        - You can still access your content until the billing period ends
        - Your data will be safely stored
        - You can reactivate anytime

        Thank you for being part of {settings.PROJECT_NAME}!

        Best regards,
        The {settings.PROJECT_NAME} Team
        """

        return self.send_email(user_email, subject, html_content, text_content)

# Create global email service instance
email_service = EmailService()
