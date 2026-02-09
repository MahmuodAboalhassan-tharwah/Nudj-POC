"""
Audit Service

TASK-012: Append-only audit logging for security events.

Features:
- Log all auth events
- Query and filter logs
- CSV export for compliance
- 5-year retention support
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from io import StringIO
import csv

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.app.common.models import AuditLog, AuditEventType


class AuditService:
    """
    Audit logging service.
    
    Provides append-only logging for security and compliance.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def log(
        self,
        event_type: AuditEventType,
        ip_address: str,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        user_agent: Optional[str] = None,
        organization_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """
        Log an audit event.
        
        Args:
            event_type: Type of event
            ip_address: Client IP
            user_id: User ID (if known)
            email: User email (for failed logins with unknown user)
            user_agent: Client user agent
            organization_id: Organization context
            details: Additional event-specific details
            
        Returns:
            Created AuditLog entry
        """
        audit_log = AuditLog(
            event_type=event_type,
            user_id=user_id,
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            organization_id=organization_id,
            details=details,
        )
        
        self.session.add(audit_log)
        await self.session.flush()
        
        return audit_log

    async def log_login_success(
        self,
        user_id: str,
        email: str,
        ip_address: str,
        user_agent: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> AuditLog:
        """Log successful login."""
        return await self.log(
            event_type=AuditEventType.LOGIN_SUCCESS,
            user_id=user_id,
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            organization_id=organization_id,
        )

    async def log_login_failed(
        self,
        email: str,
        ip_address: str,
        user_agent: Optional[str] = None,
        user_id: Optional[str] = None,
        reason: str = "invalid_credentials",
    ) -> AuditLog:
        """Log failed login attempt."""
        return await self.log(
            event_type=AuditEventType.LOGIN_FAILED,
            user_id=user_id,
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"reason": reason},
        )

    async def log_role_change(
        self,
        user_id: str,
        changed_by: str,
        old_role: str,
        new_role: str,
        ip_address: str,
    ) -> AuditLog:
        """Log role change."""
        return await self.log(
            event_type=AuditEventType.ROLE_CHANGED,
            user_id=user_id,
            ip_address=ip_address,
            details={
                "changed_by": changed_by,
                "old_role": old_role,
                "new_role": new_role,
            },
        )

    async def query_logs(
        self,
        event_type: Optional[AuditEventType] = None,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        ip_address: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[List[AuditLog], int]:
        """
        Query audit logs with filters.
        
        Args:
            event_type: Filter by event type
            user_id: Filter by user
            organization_id: Filter by organization
            start_date: Start of date range
            end_date: End of date range
            ip_address: Filter by IP
            page: Page number
            page_size: Items per page
            
        Returns:
            Tuple of (logs, total_count)
        """
        conditions = []
        
        if event_type:
            conditions.append(AuditLog.event_type == event_type)
        if user_id:
            conditions.append(AuditLog.user_id == user_id)
        if organization_id:
            conditions.append(AuditLog.organization_id == organization_id)
        if start_date:
            conditions.append(AuditLog.created_at >= start_date)
        if end_date:
            conditions.append(AuditLog.created_at <= end_date)
        if ip_address:
            conditions.append(AuditLog.ip_address == ip_address)
        
        # Build query
        query = select(AuditLog)
        if conditions:
            query = query.where(and_(*conditions))
        
        # Order by newest first
        query = query.order_by(AuditLog.created_at.desc())
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar() or 0
        
        # Get page
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        logs = result.scalars().all()
        
        return list(logs), total

    async def export_csv(
        self,
        organization_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> str:
        """
        Export audit logs as CSV.
        
        Args:
            organization_id: Filter by organization
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            CSV string
        """
        logs, _ = await self.query_logs(
            organization_id=organization_id,
            start_date=start_date,
            end_date=end_date,
            page=1,
            page_size=10000,  # Max export size
        )
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Timestamp",
            "Event Type",
            "User ID",
            "Email",
            "IP Address",
            "User Agent",
            "Organization ID",
            "Details",
        ])
        
        # Data rows
        for log in logs:
            writer.writerow([
                log.created_at.isoformat(),
                log.event_type.value,
                log.user_id or "",
                log.email or "",
                log.ip_address,
                log.user_agent or "",
                log.organization_id or "",
                str(log.details) if log.details else "",
            ])
        
        return output.getvalue()

    async def get_security_stats(
        self,
        organization_id: Optional[str] = None,
        hours: int = 24,
    ) -> Dict[str, int]:
        """
        Get security statistics for dashboard.
        
        Args:
            organization_id: Filter by organization
            hours: Time window in hours
            
        Returns:
            Dict with event counts
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        conditions = [AuditLog.created_at >= since]
        if organization_id:
            conditions.append(AuditLog.organization_id == organization_id)
        
        # Count by event type
        query = (
            select(AuditLog.event_type, func.count())
            .where(and_(*conditions))
            .group_by(AuditLog.event_type)
        )
        
        result = await self.session.execute(query)
        counts = {row[0].value: row[1] for row in result.all()}
        
        return {
            "failed_logins": counts.get("login_failed", 0),
            "successful_logins": counts.get("login_success", 0),
            "account_lockouts": counts.get("account_locked", 0),
            "rate_limit_hits": counts.get("rate_limit_exceeded", 0),
            "unauthorized_access": counts.get("unauthorized_access", 0),
        }
