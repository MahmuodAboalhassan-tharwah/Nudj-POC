/**
 * Nudj Auth Feature Types
 *
 * TASK-005: TypeScript types for authentication feature.
 *
 * Includes:
 * - User types
 * - Auth request/response DTOs
 * - Session types
 * - MFA types
 */

// =============================================================================
// Enums
// =============================================================================

export type Role = 'super_admin' | 'analyst' | 'client_admin' | 'assessor';

export type SSOProvider = 'azure_ad' | 'google';

// =============================================================================
// User Types
// =============================================================================

/**
 * Current authenticated user (from JWT).
 */
export interface CurrentUser {
  id: string;
  email: string;
  name_ar: string;
  name_en: string;
  role: Role;
  organization_id: string | null;
  mfa_enabled: boolean;
  permissions: string[];
}

/**
 * Full user details (from API).
 */
export interface User {
  id: string;
  email: string;
  name_ar: string;
  name_en: string;
  phone_sa: string | null;
  role: Role;
  organization_id: string | null;
  organization_name?: string;
  is_active: boolean;
  is_verified: boolean;
  mfa_enabled: boolean;
  sso_provider: SSOProvider | null;
  last_login_at: string | null;
  created_at: string;
  updated_at: string | null;
}

// =============================================================================
// Auth Request DTOs
// =============================================================================

/**
 * Login request.
 */
export interface LoginRequest {
  email: string;
  password: string;
  remember_me?: boolean;
}

/**
 * Registration request (with invitation token).
 */
export interface RegisterRequest {
  token: string; // Invitation token
  email: string;
  password: string;
  name_ar: string;
  name_en: string;
  phone_sa?: string;
}

/**
 * MFA verification request.
 */
export interface MFAVerifyRequest {
  code: string;
  trust_device?: boolean;
}

/**
 * Password reset request.
 */
export interface ForgotPasswordRequest {
  email: string;
}

/**
 * Reset password with token.
 */
export interface ResetPasswordRequest {
  token: string;
  password: string;
}

/**
 * Change password (authenticated).
 */
export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

/**
 * MFA setup request.
 */
export interface MFASetupRequest {
  code: string; // Verify TOTP during setup
}

// =============================================================================
// Auth Response DTOs
// =============================================================================

/**
 * Login response (could require MFA).
 */
export interface LoginResponse {
  requires_mfa: boolean;
  mfa_token?: string; // Temporary token for MFA step
  access_token?: string;
  refresh_token?: string;
  token_type?: string;
  expires_in?: number;
  user?: CurrentUser;
}

/**
 * Token refresh response.
 */
export interface TokenRefreshResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

/**
 * MFA setup response.
 */
export interface MFASetupResponse {
  secret: string;
  qr_code_uri: string;
  backup_codes: string[];
}

/**
 * Generic success response.
 */
export interface SuccessResponse {
  success: boolean;
  message_en: string;
  message_ar: string;
}

// =============================================================================
// Invitation Types
// =============================================================================

/**
 * Invitation details (for registration page).
 */
export interface Invitation {
  token: string;
  email: string;
  role: Role;
  organization_name: string | null;
  expires_at: string;
  is_valid: boolean;
}

// =============================================================================
// Session Types
// =============================================================================

/**
 * Active session info.
 */
export interface Session {
  id: string;
  ip_address: string;
  user_agent: string;
  last_activity_at: string;
  is_current: boolean;
}

// =============================================================================
// SSO Types
// =============================================================================

/**
 * SSO initiation response.
 */
export interface SSOInitResponse {
  authorization_url: string;
}

/**
 * SSO callback result.
 */
export interface SSOCallbackResult {
  success: boolean;
  access_token?: string;
  refresh_token?: string;
  user?: CurrentUser;
  error_code?: string;
}

// =============================================================================
// Password Strength
// =============================================================================

/**
 * Password validation result.
 */
export interface PasswordValidation {
  is_valid: boolean;
  strength: 'weak' | 'fair' | 'strong' | 'very_strong';
  requirements: {
    min_length: boolean;
    has_uppercase: boolean;
    has_number: boolean;
    has_special: boolean;
  };
}

// =============================================================================
// Auth State
// =============================================================================

/**
 * Auth store state.
 */
export interface AuthState {
  user: CurrentUser | null;
  access_token: string | null;
  refresh_token: string | null;
  is_authenticated: boolean;
  is_loading: boolean;
  mfa_pending: boolean;
  mfa_token: string | null;
  error: AuthError | null;
}

/**
 * Auth error.
 */
export interface AuthError {
  code: string;
  message_en: string;
  message_ar: string;
}

// =============================================================================
// Form Props Types
// =============================================================================

/**
 * Login form state.
 */
export interface LoginFormState {
  email: string;
  password: string;
  remember_me: boolean;
}

/**
 * Registration form state.
 */
export interface RegisterFormState {
  email: string;
  password: string;
  confirm_password: string;
  name_ar: string;
  name_en: string;
  phone_sa: string;
}

/**
 * MFA input state.
 */
export interface MFAFormState {
  code: string;
  trust_device: boolean;
}
