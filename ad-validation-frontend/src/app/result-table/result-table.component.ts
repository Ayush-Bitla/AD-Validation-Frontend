import { CommonModule } from '@angular/common';
import { Component, Input, computed, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatTableModule } from '@angular/material/table';

import { ConfigureColumnsDialogComponent } from '../configure-columns-dialog/configure-columns-dialog.component';
import { ValidationIssue } from '../models';

@Component({
    selector: 'app-result-table',
    standalone: true,
    imports: [CommonModule, MatTableModule, MatPaginatorModule, MatIconModule, MatButtonModule, MatFormFieldModule, MatInputModule, MatDialogModule],
    templateUrl: './result-table.component.html',
    styleUrls: ['./result-table.component.css']
})
export class ResultTableComponent {
    private readonly dialog = inject(MatDialog);

    @Input() set rows(value: ValidationIssue[]) {
        this.allRows.set(value ?? []);
        this.pageIndex.set(0);
    }

    @Input() title = 'Results';

    readonly allRows = signal<ValidationIssue[]>([]);
    readonly pageIndex = signal(0);
    readonly pageSize = signal(10);
    readonly search = signal('');

    readonly filteredRows = computed(() => {
        const query = this.search().trim().toLowerCase();
        const source = this.allRows();
        if (!query) {
            return source;
        }
        return source.filter((row) => {
            const haystack = `${row.account} ${row.reason} ${row.status ?? ''}`.toLowerCase();
            return haystack.includes(query);
        });
    });

    readonly pagedRows = computed(() => {
        const start = this.pageIndex() * this.pageSize();
        return this.filteredRows().slice(start, start + this.pageSize());
    });

    readonly pageCount = computed(() => Math.max(1, Math.ceil(this.filteredRows().length / this.pageSize())));

    get totalRows(): number {
        return this.filteredRows().length;
    }

    get rangeText(): string {
        const total = this.totalRows;
        if (!total) {
            return '0 – 0 of 0';
        }
        const from = this.pageIndex() * this.pageSize() + 1;
        const to = Math.min(from + this.pageSize() - 1, total);
        return `${from} – ${to} of ${total}`;
    }

    trackByAccount(index: number, row: ValidationIssue): string {
        return row.account ?? `${index}`;
    }

    statusChip(row: ValidationIssue): string {
        if (row.status === 'SHOULD DISABLE') {
            return 'SHOULD DISABLE';
        }
        if (row.status === 'N/A') {
            return 'N/A';
        }
        return row.status ?? 'FAIL';
    }

    chipClass(row: ValidationIssue): string {
        if (row.status === 'N/A') {
            return 'chip warning';
        }
        if (row.status === 'SHOULD DISABLE') {
            return 'chip warning';
        }
        return 'chip danger';
    }

    onPageChange(event: PageEvent): void {
        this.pageSize.set(event.pageSize);
        this.pageIndex.set(event.pageIndex);
    }

    onSearch(event: Event): void {
        const target = event.target as HTMLInputElement;
        this.search.set(target.value);
        this.pageIndex.set(0);
    }

    openColumnsDialog(): void {
        this.dialog.open(ConfigureColumnsDialogComponent, {
            width: '640px',
            disableClose: false,
            autoFocus: true
        });
    }
}
