"""
Test script to verify all imports work correctly.
"""
import sys
import os

# Set UTF-8 encoding for console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

sys.path.insert(0, r"c:\Work\PoCs\Nudj-POC")

print("Testing imports...")

# Test 1: Config
print("1. Testing config...")
try:
    from src.backend.config import settings
    print(f"   [OK] Config loaded: {settings.APP_NAME}")
except Exception as e:
    print(f"   [FAIL] Config failed: {e}")
    sys.exit(1)

# Test 2: Database
print("2. Testing database...")
try:
    from src.backend.database import get_db, get_engine, Base
    print("   [OK] Database imports successful")
except Exception as e:
    print(f"   [FAIL] Database failed: {e}")
    sys.exit(1)

# Test 3: Common models and exceptions
print("3. Testing common modules...")
try:
    from src.backend.app.common.models import TimestampMixin
    from src.backend.app.common.exceptions import NudjException, AppException
    from src.backend.app.common.middleware import RateLimitMiddleware
    print("   [OK] Common modules successful")
except Exception as e:
    print(f"   [FAIL] Common modules failed: {e}")
    sys.exit(1)

# Test 4: Auth module
print("4. Testing auth module...")
try:
    from src.backend.app.auth.models import User, Role
    from src.backend.app.auth.dependencies import get_current_user
    from src.backend.app.auth.router import router as auth_router
    print("   [OK] Auth module successful")
except Exception as e:
    print(f"   [FAIL] Auth module failed: {e}")
    sys.exit(1)

# Test 5: Organizations
print("5. Testing organizations module...")
try:
    from src.backend.app.organizations.router import router as org_router
    print("   [OK] Organizations module successful")
except Exception as e:
    print(f"   [FAIL] Organizations module failed: {e}")
    sys.exit(1)

# Test 6: Assessments
print("6. Testing assessments module...")
try:
    from src.backend.app.assessments.router import router as assess_router
    print("   [OK] Assessments module successful")
except Exception as e:
    print(f"   [FAIL] Assessments module failed: {e}")
    sys.exit(1)

# Test 7: Main app
print("7. Testing main app...")
try:
    from src.backend.main import app
    print("   [OK] Main app imported successfully!")
    print(f"\n[SUCCESS] All imports successful! App title: {app.title}")
except Exception as e:
    print(f"   [FAIL] Main app failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*50)
print("SUCCESS! Ready to start server.")
print("="*50)
