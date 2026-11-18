import { CommonModule } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import * as XLSX from 'xlsx';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTabsModule } from '@angular/material/tabs';

import { ConfigureColumnsDialogComponent } from '../configure-columns-dialog/configure-columns-dialog.component';
import { UploadSelection, ValidationIssue, ValidationResponse } from '../models';
import { ResultTableComponent } from '../result-table/result-table.component';
import { SummaryCardsComponent } from '../summary-cards/summary-cards.component';
import { UploadBoxComponent } from '../upload-box/upload-box.component';
import { ValidationService } from '../validation.service';

@Component({
    selector: 'app-validation-page',
    standalone: true,
    imports: [
        CommonModule,
        MatButtonModule,
        MatIconModule,
        MatTabsModule,
        MatDialogModule,
        MatProgressSpinnerModule,
        UploadBoxComponent,
        SummaryCardsComponent,
        ResultTableComponent
    ],
    templateUrl: './validation-page.component.html',
    styleUrls: ['./validation-page.component.css']
})
export class ValidationPageComponent {
    private readonly validationService = inject(ValidationService);
    private readonly dialog = inject(MatDialog);

    readonly uploads = signal<Record<'onprem' | 'azure' | 'accounts', UploadSelection>>({
        onprem: { file: null, sheet: '', error: null, valid: false },
        azure: { file: null, sheet: '', error: null, valid: false },
        accounts: { file: null, sheet: '', error: null, valid: false }
    });

    readonly results = signal<ValidationResponse | null>(null);
    readonly errorBanner = signal<string | null>(null);
    readonly activeTabIndex = signal(0);
    readonly isRunning = signal(false);

    readonly tabs = [
        { key: 'dc', label: '11 DC fails', icon: 'lan' },
        { key: 'name', label: 'Name mismatch', icon: 'merge_type' },
        { key: 'inactive', label: 'Should disable', icon: 'warning' },
        { key: 'lastLogin', label: 'Login 30+ days', icon: 'history' },
        { key: 'azure', label: 'Not in Azure', icon: 'cloud_off' }
    ] as const;

    readonly ready = computed(() => Object.values(this.uploads()).every((entry) => entry.valid));

    readonly currentRows = computed<ValidationIssue[]>(() => {
        const response = this.results();
        if (!response) {
            return [];
        }
        const key = this.tabs[this.activeTabIndex()].key;
        return response[key] ?? [];
    });

    readonly currentSummary = computed(() => this.results()?.summary ?? {
        totalAccounts: 0,
        dc: 0,
        name: 0,
        inactive: 0,
        lastLogin: 0,
        azure: 0
    });

    onFileChange(kind: 'onprem' | 'azure' | 'accounts', file: File): void {
        const isAllowed = /\.(csv|xlsx)$/i.test(file.name);
        const next: UploadSelection = {
            file,
            sheet: this.uploads()[kind].sheet,
            error: isAllowed ? null : 'Only .csv and .xlsx files are allowed.',
            valid: isAllowed
        };

        this.uploads.update((state) => ({ ...state, [kind]: next }));
        if (!isAllowed) {
            this.errorBanner.set(null);
        }
    }

    onSheetChange(kind: 'onprem' | 'azure' | 'accounts', value: string): void {
        this.uploads.update((state) => ({
            ...state,
            [kind]: {
                ...state[kind],
                sheet: value
            }
        }));
    }

    clearUpload(kind: 'onprem' | 'azure' | 'accounts'): void {
        this.uploads.update((state) => ({
            ...state,
            [kind]: { file: null, sheet: '', error: null, valid: false }
        }));
        this.errorBanner.set(null);
        this.results.set(null);
    }

    newComparison(): void {
        this.uploads.set({
            onprem: { file: null, sheet: '', error: null, valid: false },
            azure: { file: null, sheet: '', error: null, valid: false },
            accounts: { file: null, sheet: '', error: null, valid: false }
        });
        this.results.set(null);
        this.errorBanner.set(null);
        this.activeTabIndex.set(0);
    }

    runValidation(): void {
        if (!this.ready()) {
            return;
        }

        const formData = new FormData();
        const uploads = this.uploads();

        formData.append('onprem', uploads.onprem.file as File);
        formData.append('azure', uploads.azure.file as File);
        formData.append('accounts', uploads.accounts.file as File);

        if (uploads.onprem.sheet) {
            formData.append('onprem_sheet', uploads.onprem.sheet.trim());
        }
        if (uploads.azure.sheet) {
            formData.append('azure_sheet', uploads.azure.sheet.trim());
        }
        if (uploads.accounts.sheet) {
            formData.append('accounts_sheet', uploads.accounts.sheet.trim());
        }

        this.errorBanner.set(null);
        this.isRunning.set(true);
        this.validationService.runValidation(formData).subscribe({
            next: (response) => {
                this.results.set(response);
                this.isRunning.set(false);
                this.activeTabIndex.set(0);
                setTimeout(() => {
                    const element = document.getElementById('results-section');
                    element?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 50);
            },
            error: (err) => {
                this.isRunning.set(false);
                this.errorBanner.set(err?.error?.detail || 'The server could not complete the comparison.');
            }
        });
    }

    openColumnsDialog(): void {
        this.dialog.open(ConfigureColumnsDialogComponent, {
            width: '640px',
            disableClose: false
        });
    }

    exportToExcel(): void {
        const rows = this.currentRows();
        const workbook = XLSX.utils.book_new();
        const sheet = XLSX.utils.json_to_sheet(rows.map((row) => ({
            'Account ID': row.account,
            Result: row.status ?? 'FAIL',
            Reason: row.reason
        })));
        XLSX.utils.book_append_sheet(workbook, sheet, 'Validation Results');
        XLSX.writeFile(workbook, `ad-validation-${this.tabs[this.activeTabIndex()].key}.xlsx`);
    }

    exportToHtml(): void {
        const rows = this.currentRows();
        const html = `
      <html><head><meta charset="UTF-8" /><title>AD Validation Results</title></head>
      <body>
      <table cellpadding="8" border="1" cellspacing="0">
        <thead><tr><th>ACCOUNT ID</th><th>RESULT</th><th>REASON</th></tr></thead>
        <tbody>
          ${rows.map((row) => `<tr><td>${row.account}</td><td>${row.status ?? 'FAIL'}</td><td>${row.reason}</td></tr>`).join('') || '<tr><td colspan="3">No data</td></tr>'}
        </tbody>
      </table>
      </body></html>
    `;

        const blob = new Blob([html], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = `ad-validation-${this.tabs[this.activeTabIndex()].key}.html`;
        anchor.click();
        URL.revokeObjectURL(url);
    }
}
