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
        
        # Configure fastapi-mail (only if not in simple mock mode)
        # For simplicity in this POC, we'll focus on a robust "Mock" vs "SMTP" switch
        self.mock_mode = settings.ENVIRONMENT == "development" and not settings.SENDGRID_API_KEY
        
        if not self.mock_mode:
             self.conf = ConnectionConfig(
                MAIL_USERNAME=settings.SENDGRID_API_KEY or "apikey", # SendGrid uses generic username
                MAIL_PASSWORD=settings.SENDGRID_API_KEY,
                MAIL_FROM=settings.EMAIL_FROM_ADDRESS,
                MAIL_PORT=587,
                MAIL_SERVER="smtp.sendgrid.net",
                MAIL_STARTTLS=True,
                MAIL_SSL_TLS=False,
                USE_CREDENTIALS=True,
                VALIDATE_CERTS=True,
                TEMPLATE_FOLDER=self.template_dir
            )
             self.fastmail = FastMail(self.conf)

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
