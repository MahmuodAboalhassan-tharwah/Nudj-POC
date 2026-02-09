"""
Seed script to create initial super admin user - FIXED VERSION

Usage:
    cd c:/Work/PoCs/Nudj-POC
    PYTHONPATH="c:/Work/PoCs/Nudj-POC" py src/backend/seed_admin.py
"""
import asyncio
import sys
import uuid
from sqlalchemy import select

# Add project root to path
sys.path.insert(0, r"c:\Work\PoCs\Nudj-POC")

from src.backend.database import get_engine, Base
from src.backend.app.auth.models import User, Role
from src.backend.app.auth.password_service import PasswordService
from src.backend.database import get_async_session

# Import all models to ensure tables exist
from src.backend.app.common import models as common_models
from src.backend.app.auth import models as auth_models
try:
    from src.backend.app.comments import models as comments_models
except: pass
try:
    from src.backend.app.delegations import models as delegations_models
except: pass


async def create_super_admin():
    """Create the first super admin user."""
    print("[SEED] Starting database seed...")
    print("-" * 50)

    # Ensure all tables are created first
    print("[INFO] Creating database tables...")
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] Database tables created")
    print()

    async for session in get_async_session():
        try:
            # Check if super admin already exists
            result = await session.execute(
                select(User).where(User.role == Role.SUPER_ADMIN).limit(1)
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"[OK] Super admin already exists:")
                print(f"     Email: {existing.email}")
                print(f"     Name: {existing.name_en}")
                print(f"     ID: {existing.id}")
                print()
                print("=" * 50)
                print("LOGIN CREDENTIALS:")
                print("=" * 50)
                print(f"Email:    {existing.email}")
                print(f"Password: Nudj@2026Admin")
                print("=" * 50)
                return

            # Create super admin
            print("[INFO] Creating super admin user...")
            password_service = PasswordService()
            password_hash = password_service.hash_password("Nudj@2026Admin")

            admin = User(
                id=str(uuid.uuid4()),
                email="admin@nudj.sa",
                password_hash=password_hash,
                name_ar="مسؤول النظام",
                name_en="Super Admin",
                role=Role.SUPER_ADMIN,
                organization_id=None,  # Super admin has no organization
                is_active=True,
                is_verified=True,
                mfa_enabled=False,
                failed_login_attempts=0,
            )

            session.add(admin)
            await session.commit()

            print()
            print("=" * 50)
            print("[SUCCESS] Super admin created successfully!")
            print("=" * 50)
            print(f"Email:    admin@nudj.sa")
            print(f"Password: Nudj@2026Admin")
            print(f"ID:       {admin.id}")
            print("=" * 50)
            print()
            print("[WARNING] IMPORTANT: Change this password immediately after first login!")
            print()
            print("[INFO] You can now login at: http://localhost:5174/login")
            print()

        except Exception as e:
            print(f"\n[ERROR] Error creating super admin: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            raise
        finally:
            await session.close()
            return  # Exit after first iteration


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("Nudj Platform - Database Seed Script (FIXED)")
    print("=" * 50 + "\n")

    try:
        asyncio.run(create_super_admin())
        print("\n[DONE] Seed completed successfully!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FAIL] Seed failed: {e}\n")
        sys.exit(1)
