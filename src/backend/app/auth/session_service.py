"""
Session Service

TASK-011: User session management with Redis for real-time tracking.

Features:
- Session creation and tracking
- Activity-based timeout
- Session listing and revocation
- Redis for fast lookups
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import hashlib
import secrets

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.config import settings
from src.backend.app.auth.models import UserSession


class SessionService:
    """
    User session management service.
    
    Tracks active sessions with timeout based on inactivity.
    Uses Redis for real-time activity tracking (placeholder for POC).
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.timeout_minutes = settings.SESSION_TIMEOUT_MINUTES

    async def create_session(
        self,
        user_id: str,
        ip_address: str,
        user_agent: Optional[str] = None,
        timeout_minutes: Optional[int] = None,
    ) -> tuple[str, UserSession]:
        """
        Create a new user session.
        
        Args:
            user_id: User's ID
            ip_address: Client IP address
            user_agent: Client user agent string
            timeout_minutes: Custom timeout (optional)
            
        Returns:
            Tuple of (session_token, UserSession)
        """
        # Generate session token
        raw_token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(raw_token)
        
        # Calculate expiry
        timeout = timeout_minutes or self.timeout_minutes
        # Validate timeout bounds
        timeout = max(settings.SESSION_TIMEOUT_MIN, 
                     min(timeout, settings.SESSION_TIMEOUT_MAX))
        
        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=timeout)
        
        # Create session record
        user_session = UserSession(
            user_id=user_id,
            session_token_hash=token_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            last_activity_at=now,
            expires_at=expires_at,
        )
        
        self.session.add(user_session)
        await self.session.flush()
        
        return raw_token, user_session

    async def validate_session(
        self,
        session_token: str,
        update_activity: bool = True,
    ) -> Optional[UserSession]:
        """
        Validate a session token.
        
        Args:
            session_token: The raw session token
            update_activity: Whether to update last_activity_at
            
        Returns:
            UserSession if valid, None otherwise
        """
        token_hash = self._hash_token(session_token)
        
        result = await self.session.execute(
            select(UserSession).where(
                UserSession.session_token_hash == token_hash
            )
        )
        user_session = result.scalar_one_or_none()
        
        if not user_session:
            return None
        
        now = datetime.utcnow()
        
        # Check if expired
        if user_session.expires_at < now:
            return None
        
        # Check inactivity timeout
        inactive_since = now - user_session.last_activity_at
        if inactive_since > timedelta(minutes=self.timeout_minutes):
            return None
        
        # Update activity timestamp
        if update_activity:
            user_session.last_activity_at = now
            # Extend expiry on activity
            user_session.expires_at = now + timedelta(minutes=self.timeout_minutes)
        
        return user_session

    async def get_user_sessions(
        self,
        user_id: str,
        active_only: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Get all sessions for a user.
        
        Args:
            user_id: User's ID
            active_only: Only return active (non-expired) sessions
            
        Returns:
            List of session info dicts
        """
        query = select(UserSession).where(UserSession.user_id == user_id)
        
        if active_only:
            now = datetime.utcnow()
            query = query.where(UserSession.expires_at > now)
        
        result = await self.session.execute(query)
        sessions = result.scalars().all()
        
        return [
            {
                "id": s.id,
                "ip_address": s.ip_address,
                "user_agent": s.user_agent,
                "last_activity_at": s.last_activity_at.isoformat(),
                "created_at": s.created_at.isoformat(),
            }
            for s in sessions
        ]

    async def revoke_session(
        self,
        session_id: str,
        user_id: str,
    ) -> bool:
        """
        Revoke a specific session.
        
        Args:
            session_id: Session ID to revoke
            user_id: User ID (for authorization check)
            
        Returns:
            True if session was revoked
        """
        result = await self.session.execute(
            delete(UserSession).where(
                UserSession.id == session_id,
                UserSession.user_id == user_id,
            )
        )
        
        return result.rowcount > 0

    async def revoke_all_sessions(
        self,
        user_id: str,
        except_current: Optional[str] = None,
    ) -> int:
        """
        Revoke all sessions for a user.
        
        Args:
            user_id: User's ID
            except_current: Session ID to keep (current session)
            
        Returns:
            Number of sessions revoked
        """
        query = delete(UserSession).where(UserSession.user_id == user_id)
        
        if except_current:
            query = query.where(UserSession.id != except_current)
        
        result = await self.session.execute(query)
        
        return result.rowcount

    async def cleanup_expired_sessions(self) -> int:
        """
        Delete all expired sessions.
        
        Should be run periodically via scheduled task.
        
        Returns:
            Number of sessions cleaned up
        """
        result = await self.session.execute(
            delete(UserSession).where(
                UserSession.expires_at < datetime.utcnow()
            )
        )
        
        return result.rowcount

    def _hash_token(self, token: str) -> str:
        """Hash a session token for storage."""
        return hashlib.sha256(token.encode()).hexdigest()


# Redis-based real-time session tracking (placeholder)
class RedisSessionTracker:
    """
    Redis session tracker for real-time activity.
    
    NOTE: This is a placeholder for POC. In production, use Redis
    for fast session lookups and activity tracking.
    """
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}  # In-memory placeholder

    async def set_activity(self, session_id: str, user_id: str) -> None:
        """Record session activity in Redis."""
        self._cache[session_id] = {
            "user_id": user_id,
            "last_activity": datetime.utcnow().isoformat(),
        }

    async def get_activity(self, session_id: str) -> Optional[datetime]:
        """Get last activity time from Redis."""
        data = self._cache.get(session_id)
        if data:
            return datetime.fromisoformat(data["last_activity"])
        return None

    async def delete_session(self, session_id: str) -> None:
        """Remove session from Redis."""
        self._cache.pop(session_id, None)


# Global tracker instance
redis_tracker = RedisSessionTracker()
