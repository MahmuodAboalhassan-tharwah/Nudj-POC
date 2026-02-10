"""
Test Email Service Script

Sends a test email to verify Office365 SMTP configuration.

Usage:
    venv/Scripts/python.exe test_email_send.py
"""
import asyncio
import sys
from datetime import datetime
import uuid

sys.path.insert(0, r"C:\Users\mahmu\PycharmProjects\Tharwty-projects\POC")

# Configure output encoding
sys.stdout.reconfigure(encoding='utf-8')

from src.backend.app.notifications.email_service import email_service
from src.backend.config import settings


async def send_test_email():
    """Send a test email to verify configuration."""
    print("\n" + "="*70)
    print("Nudj Platform - Email Service Test")
    print("="*70 + "\n")

    # Email details
    recipient_email = "mahmuodaboalhassan@gmail.com"
    recipient_name = "Mahmoud"

    print("📧 Email Configuration:")
    print(f"   Provider:     {settings.EMAIL_PROVIDER}")
    print(f"   SMTP Server:  {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    print(f"   From:         {settings.EMAIL_FROM_ADDRESS}")
    print(f"   To:           {recipient_email}")
    print(f"   TLS:          {settings.EMAIL_USE_TLS}")
    print()

    # Check if in mock mode
    if email_service.mock_mode:
        print("⚠️  WARNING: Email service is in MOCK MODE")
        print("   Emails will be logged to console, not actually sent.")
        print("   This usually means email credentials are not configured.")
        print()
    else:
        print("✅ Email service is configured for real sending")
        print()

    print("Sending test email...")
    print("-"*70)

    try:
        # Prepare email context
        context = {
            "recipient_name": recipient_name,
            "sent_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "test_id": str(uuid.uuid4())[:8].upper(),
        }

        # Send email
        result = await email_service.send_email(
            recipients=[recipient_email],
            subject="✅ Nudj Platform - Email Service Test Successful",
            template_name="test_email.html",
            context=context
        )

        print()
        if result:
            print("="*70)
            print("✅ SUCCESS! Email sent successfully!")
            print("="*70)
            print()
            print("📬 Email Details:")
            print(f"   To:      {recipient_email}")
            print(f"   Subject: ✅ Nudj Platform - Email Service Test Successful")
            print(f"   Status:  Sent ✅")
            print()
            print("📨 Please check your inbox (and spam folder) at:")
            print(f"   {recipient_email}")
            print()
            print("⏰ It may take a few moments for the email to arrive.")
            print()

            if email_service.mock_mode:
                print("ℹ️  Note: Email was logged to console (MOCK MODE)")
            else:
                print("✉️  Email was sent via Office365 SMTP")
            print()
        else:
            print("❌ FAILED: Email sending failed!")
            print("   Check the error logs above for details.")
            print()

    except Exception as e:
        print()
        print("="*70)
        print("❌ ERROR: Failed to send email")
        print("="*70)
        print(f"Error: {e}")
        print()
        print("Troubleshooting:")
        print("1. Check Office365 SMTP credentials in .env")
        print("2. Verify noreply@thrwty.com mailbox exists and is active")
        print("3. Check if SMTP is enabled for the account")
        print("4. Verify password is correct")
        print("5. Check if 2FA/app password is required")
        print()
        import traceback
        traceback.print_exc()

    print("="*70)


if __name__ == "__main__":
    try:
        asyncio.run(send_test_email())
        print("\n✅ Test completed!\n")
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}\n")
        sys.exit(1)
