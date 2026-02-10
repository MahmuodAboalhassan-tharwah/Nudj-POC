"""Quick script to create superuser without model issues."""
import asyncio
import sys
import uuid
from sqlalchemy import select, text

sys.path.insert(0, r"C:\Users\mahmu\PycharmProjects\Tharwty-projects\POC")

from src.backend.database import get_async_session

async def create_super_admin():
    """Create super admin user directly via SQL."""

    async for session in get_async_session():
        try:
            # Check if super admin exists
            result = await session.execute(
                text("SELECT email FROM users WHERE role = 'super_admin' LIMIT 1")
            )
            existing = result.fetchone()

            if existing:
                print(f"✅ Super admin already exists: {existing[0]}")
                print("\n" + "="*50)
                print("LOGIN CREDENTIALS:")
                print("="*50)
                print(f"Email:    {existing[0]}")
                print(f"Password: Nudj@2026Admin")
                print("="*50)
                return

            # Import password service
            from src.backend.app.auth.password_service import PasswordService
            password_service = PasswordService()
            password_hash = password_service.hash_password("Nudj@2026Admin")

            # Create super admin via SQL
            admin_id = str(uuid.uuid4())
            await session.execute(
                text("""
                    INSERT INTO users (
                        id, email, password_hash, name_ar, name_en, role,
                        organization_id, is_active, is_verified, mfa_enabled,
                        failed_login_attempts, created_at
                    ) VALUES (
                        :id, :email, :password_hash, :name_ar, :name_en, :role,
                        NULL, true, true, false, 0, NOW()
                    )
                """),
                {
                    "id": admin_id,
                    "email": "admin@nudj.sa",
                    "password_hash": password_hash,
                    "name_ar": "مسؤول النظام",
                    "name_en": "Super Admin",
                    "role": "super_admin"
                }
            )
            await session.commit()

            print("\n" + "="*50)
            print("✅ SUCCESS! Super admin created!")
            print("="*50)
            print(f"Email:    admin@nudj.sa")
            print(f"Password: Nudj@2026Admin")
            print(f"ID:       {admin_id}")
            print("="*50)
            print("\n⚠️  IMPORTANT: Change this password after first login!")
            print(f"\n🌐 Login at: http://localhost:5175/login\n")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
            return

if __name__ == "__main__":
    asyncio.run(create_super_admin())
