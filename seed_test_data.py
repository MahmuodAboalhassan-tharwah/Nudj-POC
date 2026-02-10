"""
Seed Test Data Script

Creates test users with different roles and test notifications.

Usage:
    venv/Scripts/python.exe seed_test_data.py
"""
import asyncio
import sys
import uuid
from datetime import datetime
from sqlalchemy import select, text

sys.path.insert(0, r"C:\Users\mahmu\PycharmProjects\Tharwty-projects\POC")

# Configure output encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Disable SQLAlchemy logging to avoid Unicode encoding issues
import logging
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)

from src.backend.database import get_async_session
from src.backend.app.auth.models import User, Role
from src.backend.app.auth.password_service import PasswordService
from src.backend.app.organizations.models import Organization
from src.backend.app.notifications.models import Notification, NotificationType


async def seed_test_data():
    """Create test organizations, users, and notifications."""
    print("\n" + "=" * 70)
    print("Nudj Platform - Test Data Seed Script")
    print("=" * 70 + "\n")

    password_service = PasswordService()
    # Same password for all test users for easy testing
    test_password = "Test@2026"
    test_password_hash = password_service.hash_password(test_password)

    async for session in get_async_session():
        try:
            # ================================================================
            # Step 1: Create Test Organizations
            # ================================================================
            print("[1/4] Creating test organizations...")

            # Check if organizations already exist
            result = await session.execute(select(Organization).limit(1))
            existing_org = result.scalar_one_or_none()

            if existing_org:
                print(f"     ✓ Organizations already exist, using existing data")
                result = await session.execute(select(Organization).limit(3))
                orgs = result.scalars().all()
            else:
                # Create test organizations
                org1 = Organization(
                    id=uuid.uuid4(),
                    name_ar="شركة التقنية المتقدمة",
                    name_en="Advanced Technology Company",
                    cr_number="1010123456",
                    sector="Information Technology",
                    size="Medium",
                    region="Riyadh",
                    is_active=True,
                )

                org2 = Organization(
                    id=uuid.uuid4(),
                    name_ar="مؤسسة الموارد البشرية المتميزة",
                    name_en="Excellence HR Solutions",
                    cr_number="1010234567",
                    sector="Professional Services",
                    size="Small",
                    region="Jeddah",
                    is_active=True,
                )

                org3 = Organization(
                    id=uuid.uuid4(),
                    name_ar="مجموعة الابتكار الصناعي",
                    name_en="Industrial Innovation Group",
                    cr_number="1010345678",
                    sector="Manufacturing",
                    size="Enterprise",
                    region="Dammam",
                    is_active=True,
                )

                session.add_all([org1, org2, org3])
                await session.commit()

                orgs = [org1, org2, org3]
                print(f"     ✓ Created 3 test organizations")

            print()

            # ================================================================
            # Step 2: Create Test Users with Different Roles
            # ================================================================
            print("[2/4] Creating test users...")

            # Check existing users
            result = await session.execute(select(User))
            existing_users = {user.email: user for user in result.scalars().all()}

            test_users = []

            # Super Admin (already exists)
            if "admin@nudj.sa" in existing_users:
                print(f"     ✓ Super Admin already exists: admin@nudj.sa")
                test_users.append(existing_users["admin@nudj.sa"])

            # Analyst User (works with multiple organizations)
            analyst_email = "analyst@nudj.sa"
            if analyst_email not in existing_users:
                analyst = User(
                    id=str(uuid.uuid4()),
                    email=analyst_email,
                    password_hash=test_password_hash,
                    name_ar="محلل الموارد البشرية",
                    name_en="HR Analyst",
                    phone_sa="+966501234567",
                    role=Role.ANALYST,
                    organization_id=None,  # Analysts work across organizations
                    is_active=True,
                    is_verified=True,
                    mfa_enabled=False,
                    failed_login_attempts=0,
                )
                session.add(analyst)
                test_users.append(analyst)
                print(f"     ✓ Created Analyst: {analyst_email}")
            else:
                print(f"     ✓ Analyst already exists: {analyst_email}")
                test_users.append(existing_users[analyst_email])

            # Client Admin 1 (Organization 1)
            client1_email = "admin@advtech.sa"
            if client1_email not in existing_users:
                client1 = User(
                    id=str(uuid.uuid4()),
                    email=client1_email,
                    password_hash=test_password_hash,
                    name_ar="أحمد السعيد",
                    name_en="Ahmed AlSaeed",
                    phone_sa="+966502345678",
                    role=Role.CLIENT_ADMIN,
                    organization_id=str(orgs[0].id),
                    is_active=True,
                    is_verified=True,
                    mfa_enabled=False,
                    failed_login_attempts=0,
                )
                session.add(client1)
                test_users.append(client1)
                print(f"     ✓ Created Client Admin 1: {client1_email} ({orgs[0].name_en})")
            else:
                print(f"     ✓ Client Admin 1 already exists: {client1_email}")
                test_users.append(existing_users[client1_email])

            # Client Admin 2 (Organization 2)
            client2_email = "admin@hrexcellence.sa"
            if client2_email not in existing_users:
                client2 = User(
                    id=str(uuid.uuid4()),
                    email=client2_email,
                    password_hash=test_password_hash,
                    name_ar="فاطمة العتيبي",
                    name_en="Fatima AlOtaibi",
                    phone_sa="+966503456789",
                    role=Role.CLIENT_ADMIN,
                    organization_id=str(orgs[1].id),
                    is_active=True,
                    is_verified=True,
                    mfa_enabled=False,
                    failed_login_attempts=0,
                )
                session.add(client2)
                test_users.append(client2)
                print(f"     ✓ Created Client Admin 2: {client2_email} ({orgs[1].name_en})")
            else:
                print(f"     ✓ Client Admin 2 already exists: {client2_email}")
                test_users.append(existing_users[client2_email])

            # Assessor 1 (Organization 1)
            assessor1_email = "assessor1@advtech.sa"
            if assessor1_email not in existing_users:
                assessor1 = User(
                    id=str(uuid.uuid4()),
                    email=assessor1_email,
                    password_hash=test_password_hash,
                    name_ar="سارة المحمدي",
                    name_en="Sarah AlMohammadi",
                    phone_sa="+966504567890",
                    role=Role.ASSESSOR,
                    organization_id=str(orgs[0].id),
                    is_active=True,
                    is_verified=True,
                    mfa_enabled=False,
                    failed_login_attempts=0,
                )
                session.add(assessor1)
                test_users.append(assessor1)
                print(f"     ✓ Created Assessor 1: {assessor1_email} ({orgs[0].name_en})")
            else:
                print(f"     ✓ Assessor 1 already exists: {assessor1_email}")
                test_users.append(existing_users[assessor1_email])

            # Assessor 2 (Organization 2)
            assessor2_email = "assessor@hrexcellence.sa"
            if assessor2_email not in existing_users:
                assessor2 = User(
                    id=str(uuid.uuid4()),
                    email=assessor2_email,
                    password_hash=test_password_hash,
                    name_ar="خالد الشمري",
                    name_en="Khaled AlShammari",
                    phone_sa="+966505678901",
                    role=Role.ASSESSOR,
                    organization_id=str(orgs[1].id),
                    is_active=True,
                    is_verified=True,
                    mfa_enabled=False,
                    failed_login_attempts=0,
                )
                session.add(assessor2)
                test_users.append(assessor2)
                print(f"     ✓ Created Assessor 2: {assessor2_email} ({orgs[1].name_en})")
            else:
                print(f"     ✓ Assessor 2 already exists: {assessor2_email}")
                test_users.append(existing_users[assessor2_email])

            await session.commit()
            print()

            # ================================================================
            # Step 3: Create Test Notifications
            # ================================================================
            print("[3/4] Creating test notifications...")

            # Check if notifications already exist
            result = await session.execute(select(Notification).limit(1))
            existing_notif = result.scalar_one_or_none()

            if existing_notif:
                print(f"     ✓ Notifications already exist")
            else:
                notifications = []

                for user in test_users:
                    # Welcome notification
                    notifications.append(Notification(
                        id=uuid.uuid4(),
                        user_id=uuid.UUID(user.id) if isinstance(user.id, str) else user.id,
                        title="Welcome to Nudj Platform",
                        message=f"Welcome {user.name_en}! Your account has been created successfully.",
                        type=NotificationType.SUCCESS.value,
                        link="/dashboard",
                        is_read=False,
                        created_at=datetime.utcnow(),
                    ))

                    # Role-specific notification
                    if user.role == Role.SUPER_ADMIN:
                        notifications.append(Notification(
                            id=uuid.uuid4(),
                            user_id=uuid.UUID(user.id) if isinstance(user.id, str) else user.id,
                            title="Platform Status",
                            message="All systems operational. 3 organizations are currently active.",
                            type=NotificationType.INFO.value,
                            link="/admin/dashboard",
                            is_read=False,
                            created_at=datetime.utcnow(),
                        ))

                    elif user.role == Role.ANALYST:
                        notifications.append(Notification(
                            id=uuid.uuid4(),
                            user_id=uuid.UUID(user.id) if isinstance(user.id, str) else user.id,
                            title="New Assessment Available",
                            message="A new assessment is pending your review for Advanced Technology Company.",
                            type=NotificationType.ACTION_REQUIRED.value,
                            link="/assessments",
                            is_read=False,
                            created_at=datetime.utcnow(),
                        ))

                    elif user.role == Role.CLIENT_ADMIN:
                        notifications.append(Notification(
                            id=uuid.uuid4(),
                            user_id=uuid.UUID(user.id) if isinstance(user.id, str) else user.id,
                            title="Assessment Progress",
                            message="Your organization's HR maturity assessment is 25% complete.",
                            type=NotificationType.INFO.value,
                            link="/assessments/current",
                            is_read=False,
                            created_at=datetime.utcnow(),
                        ))

                    elif user.role == Role.ASSESSOR:
                        notifications.append(Notification(
                            id=uuid.uuid4(),
                            user_id=uuid.UUID(user.id) if isinstance(user.id, str) else user.id,
                            title="Domain Assignment",
                            message="You have been assigned to assess the Recruitment domain.",
                            type=NotificationType.ACTION_REQUIRED.value,
                            link="/assessments/domains",
                            is_read=False,
                            created_at=datetime.utcnow(),
                        ))

                session.add_all(notifications)
                await session.commit()
                print(f"     ✓ Created {len(notifications)} test notifications")

            print()

            # ================================================================
            # Step 4: Display Test Credentials
            # ================================================================
            print("[4/4] Test credentials summary:")
            print()
            print("=" * 70)
            print("TEST USER CREDENTIALS")
            print("=" * 70)
            print(f"Password (all users): {test_password}")
            print("-" * 70)
            print()

            # Get fresh user data with organizations
            result = await session.execute(
                select(User).where(User.email.in_([
                    "admin@nudj.sa",
                    "analyst@nudj.sa",
                    "admin@advtech.sa",
                    "admin@hrexcellence.sa",
                    "assessor1@advtech.sa",
                    "assessor@hrexcellence.sa"
                ]))
            )
            users = result.scalars().all()

            # Get organizations for display
            result = await session.execute(select(Organization))
            orgs_dict = {str(org.id): org.name_en for org in result.scalars().all()}

            for user in users:
                org_name = orgs_dict.get(user.organization_id, "N/A")
                print(f"Role: {user.role.value.upper().replace('_', ' ')}")
                print(f"  Email:        {user.email}")
                print(f"  Name:         {user.name_en}")
                print(f"  Organization: {org_name}")
                print(f"  Status:       {'Active' if user.is_active else 'Inactive'}")
                print()

            print("=" * 70)
            print()
            print("✅ Test data seeded successfully!")
            print()
            print("📧 Email Configuration:")
            print(f"   Host:     smtp.office365.com")
            print(f"   Port:     587")
            print(f"   From:     noreply@thrwty.com")
            print(f"   TLS:      Enabled")
            print()
            print("🌐 Login at: http://localhost:5175/login")
            print()

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            raise
        finally:
            await session.close()
            return


if __name__ == "__main__":
    try:
        asyncio.run(seed_test_data())
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Seed failed: {e}")
        sys.exit(1)
