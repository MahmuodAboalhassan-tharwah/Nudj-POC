"""
Simple script to create admin user using direct SQL.
"""
import asyncio
import uuid
import sys
sys.path.insert(0, r"c:\Work\PoCs\Nudj-POC")

from src.backend.database import get_engine
from src.backend.app.auth.password_service import PasswordService
from sqlalchemy import text


async def create_admin():
    """Create admin user with direct SQL."""
    print("\n" + "=" * 60)
    print("Creating Super Admin User")
    print("=" * 60 + "\n")

    engine = get_engine()
    password_service = PasswordService()
    password_hash = password_service.hash_password("Nudj@2026Admin")
    user_id = str(uuid.uuid4())

    async with engine.begin() as conn:
        # Check if user exists
        result = await conn.execute(
            text("SELECT email FROM users WHERE email = 'admin@nudj.sa'")
        )
        existing = result.fetchone()

        if existing:
            print("[OK] Super admin already exists!")
            print("     Email: admin@nudj.sa")
            print()
            print("=" * 60)
            print("LOGIN CREDENTIALS:")
            print("=" * 60)
            print("Email:    admin@nudj.sa")
            print("Password: Nudj@2026Admin")
            print("URL:      http://localhost:5174/login")
            print("=" * 60 + "\n")
            return

        # Insert admin user (Note: enum values are UPPERCASE in DB)
        await conn.execute(
            text("""
                INSERT INTO users (
                    id, email, password_hash, name_ar, name_en,
                    role, organization_id, is_active, is_verified,
                    mfa_enabled, failed_login_attempts, created_at
                ) VALUES (
                    :id, :email, :password_hash, :name_ar, :name_en,
                    :role, NULL, TRUE, TRUE,
                    FALSE, 0, NOW()
                )
            """),
            {
                "id": user_id,
                "email": "admin@nudj.sa",
                "password_hash": password_hash,
                "name_ar": "Admin",
                "name_en": "Super Admin",
                "role": "SUPER_ADMIN",
            }
        )

        print("[SUCCESS] Super admin created successfully!")
        print()
        print("=" * 60)
        print("LOGIN CREDENTIALS:")
        print("=" * 60)
        print("Email:    admin@nudj.sa")
        print("Password: Nudj@2026Admin")
        print("User ID:  " + user_id)
        print("URL:      http://localhost:5174/login")
        print("=" * 60)
        print()
        print("[WARNING] Change this password after first login!")
        print()


if __name__ == "__main__":
    try:
        asyncio.run(create_admin())
        print("[DONE] Completed successfully!\n")
    except Exception as e:
        print(f"\n[ERROR] Failed: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
