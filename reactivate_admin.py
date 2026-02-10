"""
Reactivate Admin Account Script

Reactivates a deactivated admin account by setting is_active=True in the database.

Usage:
    venv/Scripts/python.exe reactivate_admin.py admin@nudj.sa
"""
import asyncio
import sys
from sqlalchemy import select, update

sys.path.insert(0, r"C:\Users\mahmu\PycharmProjects\Tharwty-projects\POC")

# Configure output encoding
sys.stdout.reconfigure(encoding='utf-8')

from src.backend.database import get_async_session
from src.backend.app.auth.models import User


async def reactivate_user(email: str):
    """Reactivate a deactivated user account."""
    print("\n" + "="*70)
    print("Nudj Platform - Account Reactivation")
    print("="*70 + "\n")

    async for session in get_async_session():
        try:
            # Find user
            result = await session.execute(
                select(User).where(User.email == email.lower())
            )
            user = result.scalar_one_or_none()

            if not user:
                print(f"❌ ERROR: User not found: {email}")
                print(f"   No user with email '{email}' exists in the database.")
                return False

            print(f"📧 Found user: {email}")
            print(f"   Name:     {user.name_en or user.name_ar or 'N/A'}")
            print(f"   Role:     {user.role.value}")
            print(f"   Active:   {'✅ YES' if user.is_active else '❌ NO (DEACTIVATED)'}")
            print()

            if user.is_active:
                print("✅ Account is already active!")
                print("   No action needed.")
                return True

            # Reactivate
            print("🔄 Reactivating account...")
            user.is_active = True
            user.failed_login_attempts = 0  # Reset login attempts
            user.locked_until = None  # Clear lockout

            await session.commit()

            print()
            print("="*70)
            print("✅ SUCCESS! Account reactivated!")
            print("="*70)
            print()
            print(f"📧 Email:  {email}")
            print(f"🔑 Status: ACTIVE ✅")
            print()
            print("You can now log in with this account.")
            print()

            return True

        except Exception as e:
            print()
            print("="*70)
            print("❌ ERROR: Failed to reactivate account")
            print("="*70)
            print(f"Error: {e}")
            print()
            import traceback
            traceback.print_exc()
            await session.rollback()
            return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reactivate_admin.py <email>")
        print("Example: python reactivate_admin.py admin@nudj.sa")
        sys.exit(1)

    email = sys.argv[1]

    try:
        success = asyncio.run(reactivate_user(email))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Failed: {e}\n")
        sys.exit(1)
