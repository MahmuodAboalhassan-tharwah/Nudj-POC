import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr

from src.backend.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(self.template_dir))

        # Determine if we should use mock mode
        # Mock mode if: development + no email credentials configured
        has_sendgrid = bool(settings.SENDGRID_API_KEY)
        has_smtp = bool(settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD)
        self.mock_mode = settings.ENVIRONMENT == "development" and not (has_sendgrid or has_smtp)

        if not self.mock_mode:
            # Configure based on EMAIL_PROVIDER setting
            if settings.EMAIL_PROVIDER == "smtp":
                # SMTP configuration (Office365, Gmail, etc.)
                logger.info(f"Configuring SMTP email: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
                self.conf = ConnectionConfig(
                    MAIL_USERNAME=settings.EMAIL_HOST_USER,
                    MAIL_PASSWORD=settings.EMAIL_HOST_PASSWORD,
                    MAIL_FROM=settings.EMAIL_FROM_ADDRESS,
                    MAIL_FROM_NAME=settings.EMAIL_FROM_NAME,
                    MAIL_PORT=settings.EMAIL_PORT,
                    MAIL_SERVER=settings.EMAIL_HOST,
                    MAIL_STARTTLS=settings.EMAIL_USE_TLS,
                    MAIL_SSL_TLS=False,
                    USE_CREDENTIALS=True,
                    VALIDATE_CERTS=True,
                    TEMPLATE_FOLDER=self.template_dir
                )
            else:
                # SendGrid configuration
                logger.info("Configuring SendGrid email")
                self.conf = ConnectionConfig(
                    MAIL_USERNAME="apikey",  # SendGrid uses generic username
                    MAIL_PASSWORD=settings.SENDGRID_API_KEY,
                    MAIL_FROM=settings.EMAIL_FROM_ADDRESS,
                    MAIL_FROM_NAME=settings.EMAIL_FROM_NAME,
                    MAIL_PORT=587,
                    MAIL_SERVER="smtp.sendgrid.net",
                    MAIL_STARTTLS=True,
                    MAIL_SSL_TLS=False,
                    USE_CREDENTIALS=True,
                    VALIDATE_CERTS=True,
                    TEMPLATE_FOLDER=self.template_dir
                )
            self.fastmail = FastMail(self.conf)
            logger.info(f"✅ Email service configured: {settings.EMAIL_PROVIDER}")

    async def send_email(
        self, 
        recipients: List[EmailStr], 
        subject: str, 
        template_name: str, 
        context: Dict[str, Any]
    ):
        """
        Sends an email using a template.
        """
        try:
            template = self.jinja_env.get_template(template_name)
            html_content = template.render(**context)
            
            if self.mock_mode:
                logger.info(f"========== MOCK EMAIL ==========")
                logger.info(f"To: {recipients}")
                logger.info(f"Subject: {subject}")
                logger.info(f"Body: {html_content[:200]}...") # Log 1st 200 chars
                logger.info("================================")
                return True

            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                body=html_content,
                subtype=MessageType.html
            )

            await self.fastmail.send_message(message)
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {recipients}: {e}")
            return False

email_service = EmailService()
