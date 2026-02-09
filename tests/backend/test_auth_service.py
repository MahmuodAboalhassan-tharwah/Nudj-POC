import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from src.backend.app.auth.service import AuthService
from src.backend.app.auth.models import User, Role
from src.backend.app.auth.exceptions import InvalidCredentialsException, AccountLockedException

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.fixture
def auth_service(mock_session):
    return AuthService(mock_session)

@pytest.mark.asyncio
async def test_login_success(auth_service, mock_session):
    # Setup
    user = User(
        id="user-123",
        email="test@example.com",
        password_hash="hashed_password",
        role=Role.CLIENT_ADMIN,
        is_active=True,
        mfa_enabled=False
    )
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute.return_value = mock_result
    
    # Mock password verification
    with MagicMock() as mock_pw:
        from src.backend.app.auth.password_service import password_service
        password_service.verify_password = MagicMock(return_value=True)
        
        # Mock token generation
        auth_service._generate_auth_response = AsyncMock(return_value={"access_token": "token"})
        
        # Execute
        response = await auth_service.login("test@example.com", "password", "127.0.0.1")
        
        # Verify
        assert response["access_token"] == "token"
        assert user.failed_login_attempts == 0

@pytest.mark.asyncio
async def test_login_invalid_password(auth_service, mock_session):
    # Setup
    user = User(
        id="user-123",
        email="test@example.com",
        password_hash="hashed_password",
        role=Role.CLIENT_ADMIN,
        is_active=True,
        failed_login_attempts=0
    )
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute.return_value = mock_result
    
    # Mock password verification
    from src.backend.app.auth.password_service import password_service
    password_service.verify_password = MagicMock(return_value=False)
    
    # Execute & Verify
    with pytest.raises(InvalidCredentialsException):
        await auth_service.login("test@example.com", "wrong", "127.0.0.1")
    
    assert user.failed_login_attempts == 1

@pytest.mark.asyncio
async def test_login_account_locked(auth_service, mock_session):
    # Setup
    locked_until = datetime.utcnow() + timedelta(minutes=10)
    user = User(
        id="user-123",
        email="test@example.com",
        locked_until=locked_until,
        is_active=True
    )
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute.return_value = mock_result
    
    # Execute & Verify
    with pytest.raises(AccountLockedException):
        await auth_service.login("test@example.com", "password", "127.0.0.1")
