"""Check if test data was created successfully."""
import asyncio
import sys
sys.path.insert(0, r"C:\Users\mahmu\PycharmProjects\Tharwty-projects\POC")

from sqlalchemy import select
from src.backend.database import get_async_session
from src.backend.app.auth.models import User, Role
from src.backend.app.organizations.models import Organization
from src.backend.app.notifications.models import Notification

# Configure output encoding for Arabic text
sys.stdout.reconfigure(encoding='utf-8')


async def check_data():
    async for session in get_async_session():
        try:
            # Check organizations
            result = await session.execute(select(Organization))
            orgs = result.scalars().all()
            print(f"\n✓ Organizations: {len(orgs)}")
            for org in orgs:
                print(f"  - {org.name_en} ({org.name_ar})")

            # Check users
            result = await session.execute(select(User))
            users = result.scalars().all()
            print(f"\n✓ Users: {len(users)}")
            for user in users:
                print(f"  - {user.email:30s} | {user.role.value:15s} | {user.name_en}")

            # Check notifications
            result = await session.execute(select(Notification))
            notifications = result.scalars().all()
            print(f"\n✓ Notifications: {len(notifications)}")

            print("\n" + "="*70)
            print("TEST USER CREDENTIALS")
            print("="*70)
            print("Password (all test users): Test@2026")
            print("-"*70)
            print("\nTest user emails:")
            test_emails = [
                "admin@nudj.sa",
                "analyst@nudj.sa",
                "admin@advtech.sa",
                "admin@hrexcellence.sa",
                "assessor1@advtech.sa",
                "assessor@hrexcellence.sa"
            ]
            result = await session.execute(
                select(User).where(User.email.in_(test_emails))
            )
            users = result.scalars().all()
            for user in users:
                print(f"  {user.role.value:15s} | {user.email}")

            print("\n" + "="*70)

        finally:
            await session.close()
            return


if __name__ == "__main__":
    asyncio.run(check_data())
