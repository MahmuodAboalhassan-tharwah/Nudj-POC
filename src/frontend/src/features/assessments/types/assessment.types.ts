import { User } from '@/features/auth/types/auth.types';

export enum AssessmentStatus {
    DRAFT = 'DRAFT',
    IN_PROGRESS = 'IN_PROGRESS',
    UNDER_REVIEW = 'UNDER_REVIEW',
    REVISION_REQUESTED = 'REVISION_REQUESTED',
    COMPLETED = 'COMPLETED',
    ARCHIVED = 'ARCHIVED',
}

import { Comment } from '../../comments/types';

export interface Assessment {
    id: string;
    organizationId: string;
    status: AssessmentStatus;
    score: number | null;
    deadline: string | null;
    createdBy: string;
    createdAt: string;
    updatedAt: string;
    domains?: AssessmentDomain[];
}

export interface AssessmentDomain {
    id: string;
    assessmentId: string;
    domainId: number;
    weight: number;
    score: number | null;
    status: string; // PENDING, IN_PROGRESS, COMPLETED
    assigneeId: string | null;
    createdAt: string;
    updatedAt: string;
    elements?: AssessmentElementResponse[];
    assignee?: User;
}

export interface AssessmentElementResponse {
    id: string;
    domainRecordId: string;
    elementId: number;
    maturityLevel: number | null; // 1-4
    score: number | null; // 0, 33, 67, 100
    comment: string | null;
    createdAt: string;
    updatedAt: string;
    evidence?: Evidence[];
    comments?: Comment[];
}

export interface Evidence {
    id: string;
    responseId: string;
    fileName: string;
    fileUrl: string;
    mimeType: string | null;
    sizeBytes: number | null;
    uploadedBy: string;
    createdAt: string;
    updatedAt: string;
}

// Aliases for API consistency
export type AssessmentCreatePayload = CreateAssessmentPayload;
export type AssessmentResponse = Assessment;
export type AssessmentUpdatePayload = UpdateAssessmentStatusPayload;

export interface CreateAssessmentPayload {
    organizationId: string;
    deadline?: string;
    domainIds?: number[]; // Optional if we want to support subset of domains
}

export interface UpdateAssessmentStatusPayload {
    status: AssessmentStatus;
}

export interface AssignDomainPayload {
    domainId: string; // This is the record ID, not the domain number
    assigneeId: string;
}

export interface SubmitElementResponsePayload {
    elementId: number;
    maturityLevel: number;
    comment?: string;
}

export enum DelegationStatus {
    ACTIVE = 'ACTIVE',
    REVOKED = 'REVOKED',
}

export interface AssessmentDelegation {
    id: string;
    assessmentId: string;
    domainId: string | null;
    userId: string;
    createdBy: string;
    status: DelegationStatus;
    notes: string | null;
    createdAt: string;
    updatedAt: string | null;
    delegateeName?: string;
    delegatorName?: string;
    domainName?: string;
}

export interface CreateDelegationPayload {
    assessmentId: string;
    domainId?: string;
    userId: string;
    notes?: string;
}
