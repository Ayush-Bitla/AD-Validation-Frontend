export type CheckKey = 'dc' | 'name' | 'inactive' | 'lastLogin' | 'azure';

export interface ValidationIssue {
    account: string;
    reason: string;
    status?: string;
}

export interface ValidationSummary {
    totalAccounts: number;
    dc: number;
    name: number;
    inactive: number;
    lastLogin: number;
    azure: number;
}

export interface ValidationResponse {
    summary: ValidationSummary;
    dc: ValidationIssue[];
    name: ValidationIssue[];
    inactive: Array<ValidationIssue & { status?: string }>;
    lastLogin: ValidationIssue[];
    azure: ValidationIssue[];
}

export interface UploadSelection {
    file: File | null;
    sheet: string;
    error: string | null;
    valid: boolean;
}
