/**
 * Nudj Admin Feature Types
 *
 * TASK-006: TypeScript types for admin user management.
 *
 * Includes:
 * - User management DTOs
 * - Invitation management DTOs
 * - Audit log types
 * - Filter and pagination types
 */

import { Role, User } from '../../../auth/types/auth.types';

// =============================================================================
// User Management
// =============================================================================

/**
 * User list item (summary for tables).
 */
export interface UserListItem {
    id: string;
    email: string;
    name_ar: string;
    name_en: string;
    role: Role;
    organization_id: string | null;
    organization_name: string | null;
    is_active: boolean;
    mfa_enabled: boolean;
    last_login_at: string | null;
    created_at: string;
}

/**
 * User filter params.
 */
export interface UserFilter {
    search?: string;
    role?: Role;
    is_active?: boolean;
    organization_id?: string;
    page?: number;
    page_size?: number;
}

/**
 * Paginated user response.
 */
export interface PaginatedUsers {
    items: UserListItem[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
}

/**
 * Update user request.
 */
export interface UpdateUserRequest {
    role?: Role;
    is_active?: boolean;
}

// =============================================================================
// Invitation Management
// =============================================================================

/**
 * Send invitation request.
 */
export interface InviteUserRequest {
    email: string;
    role: Role;
    organization_id?: string;
    domain_ids?: string[];
    message_template?: 'default' | 'custom';
    custom_message?: string;
}

/**
 * Bulk invite request.
 */
export interface BulkInviteRequest {
    invitations: InviteUserRequest[];
}

/**
 * Bulk invite file upload format.
 */
export interface BulkInviteCSVRow {
    email: string;
    role: string;
    organization_id?: string;
    domain_ids?: string; // Comma-separated
}

/**
 * Invitation list item.
 */
export interface InvitationListItem {
    id: string;
    email: string;
    role: Role;
    organization_name: string | null;
    invited_by: string;
    invited_by_name: string;
    expires_at: string;
    is_expired: boolean;
    is_used: boolean;
    created_at: string;
}

/**
 * Invitation filter params.
 */
export interface InvitationFilter {
    status?: 'pending' | 'expired' | 'used';
    organization_id?: string;
    page?: number;
    page_size?: number;
}

/**
 * Paginated invitations response.
 */
export interface PaginatedInvitations {
    items: InvitationListItem[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
}

// =============================================================================
// Audit Log Types
// =============================================================================

/**
 * Audit event type enum.
 */
export type AuditEventType =
    | 'login_success'
    | 'login_failed'
    | 'logout'
    | 'password_changed'
    | 'password_reset_requested'
    | 'password_reset_completed'
    | 'mfa_enabled'
    | 'mfa_disabled'
    | 'mfa_verified'
    | 'mfa_failed'
    | 'user_registered'
    | 'role_changed'
    | 'user_deactivated'
    | 'user_reactivated'
    | 'invitation_sent'
    | 'invitation_accepted'
    | 'invitation_expired'
    | 'session_created'
    | 'session_expired'
    | 'session_revoked'
    | 'unauthorized_access'
    | 'account_locked'
    | 'rate_limit_exceeded'
    | 'data_export_requested'
    | 'data_deletion_requested';

/**
 * Audit log entry.
 */
export interface AuditLogEntry {
    id: string;
    event_type: AuditEventType;
    user_id: string | null;
    user_email: string | null;
    user_name: string | null;
    ip_address: string;
    user_agent: string | null;
    details: Record<string, unknown> | null;
    organization_id: string | null;
    organization_name: string | null;
    created_at: string;
}

/**
 * Audit log filter params.
 */
export interface AuditLogFilter {
    event_type?: AuditEventType;
    user_id?: string;
    organization_id?: string;
    start_date?: string;
    end_date?: string;
    ip_address?: string;
    page?: number;
    page_size?: number;
}

/**
 * Paginated audit logs response.
 */
export interface PaginatedAuditLogs {
    items: AuditLogEntry[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
}

// =============================================================================
// Organization Types (for admin context)
// =============================================================================

/**
 * Organization summary for dropdowns.
 */
export interface OrganizationSummary {
    id: string;
    name_ar: string;
    name_en: string;
    user_count: number;
    is_active: boolean;
}

// =============================================================================
// Domain Assignment Types
// =============================================================================

/**
 * HR Domain for assignment.
 */
export interface HRDomain {
    id: string;
    name_ar: string;
    name_en: string;
    description_ar?: string;
    description_en?: string;
}

/**
 * Domain assignment for assessor.
 */
export interface DomainAssignment {
    user_id: string;
    assessment_id?: string;
    domain_ids: string[];
}

/**
 * Update domain assignment request.
 */
export interface UpdateDomainAssignmentRequest {
    domain_ids: string[];
}

// =============================================================================
// Analytics Types (for admin dashboard)
// =============================================================================

/**
 * User statistics.
 */
export interface UserStats {
    total_users: number;
    active_users: number;
    users_by_role: Record<Role, number>;
    new_users_30d: number;
    mfa_enabled_count: number;
}

/**
 * Security statistics.
 */
export interface SecurityStats {
    failed_logins_24h: number;
    locked_accounts: number;
    active_sessions: number;
    rate_limit_hits_24h: number;
}

// =============================================================================
// Table Column Definitions
// =============================================================================

/**
 * Sortable column config.
 */
export interface SortConfig {
    key: string;
    direction: 'asc' | 'desc';
}

/**
 * Table action.
 */
export interface TableAction<T> {
    label_en: string;
    label_ar: string;
    icon?: string;
    variant?: 'default' | 'danger';
    onClick: (item: T) => void;
    isVisible?: (item: T) => boolean;
    isDisabled?: (item: T) => boolean;
}
