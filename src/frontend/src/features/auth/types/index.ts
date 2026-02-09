/**
 * Auth types barrel export file.
 * Exports all auth-related types and enums.
 */

// Export Role enum (not type) for usage like Role.SUPER_ADMIN
export { Role, type RoleType } from './role.enum';

// Re-export all other types from auth.types.ts, but exclude the old Role type
export type {
  SSOProvider,
  CurrentUser,
  User,
  LoginRequest,
  RegisterRequest,
  MFAVerifyRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  ChangePasswordRequest,
  MFASetupRequest,
  LoginResponse,
  TokenRefreshResponse,
  MFASetupResponse,
  SuccessResponse,
  Invitation,
  Session,
  SSOInitResponse,
  SSOCallbackResult,
  PasswordValidation,
  AuthState,
  AuthError,
  LoginFormState,
  RegisterFormState,
  MFAFormState,
} from './auth.types';
