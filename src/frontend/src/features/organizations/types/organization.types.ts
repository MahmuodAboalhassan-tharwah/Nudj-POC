export interface Organization {
    id: string;
    name_ar: string;
    name_en: string;
    cr_number?: string;
    sector?: string;
    size?: string;
    region?: string;
    logo_url?: string;
    is_active: boolean;
    created_at: string;
    updated_at?: string;
}

export interface OrganizationCreatePayload {
    name_ar: string;
    name_en: string;
    cr_number?: string;
    sector?: string;
    size?: string;
    region?: string;
    logo_url?: string;
    is_active?: boolean;
}

export interface OrganizationUpdatePayload extends Partial(OrganizationCreatePayload) { }

export interface OrganizationListParams {
    skip?: number;
    limit?: number;
}
