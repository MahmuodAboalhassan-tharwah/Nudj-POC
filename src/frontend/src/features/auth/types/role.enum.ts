/**
 * User roles enum - matches backend Role enum.
 *
 * This enum allows usage like Role.SUPER_ADMIN for better code readability
 * while maintaining compatibility with the backend API string values.
 */
export enum Role {
  SUPER_ADMIN = 'super_admin',
  ANALYST = 'analyst',
  CLIENT_ADMIN = 'client_admin',
  ASSESSOR = 'assessor',
}

/**
 * Role type alias for type checking.
 */
export type RoleType = 'super_admin' | 'analyst' | 'client_admin' | 'assessor';
