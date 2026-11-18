import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';

@Component({
    selector: 'app-configure-columns-dialog',
    standalone: true,
    imports: [CommonModule, FormsModule, MatDialogModule, MatButtonModule, MatFormFieldModule, MatInputModule, MatIconModule],
    template: `
    <h2 mat-dialog-title>Configure Columns</h2>
    <div class="config-grid" mat-dialog-content>
      <div class="panel">
        <div class="panel-header">Available Columns</div>
        <mat-form-field appearance="outline">
          <mat-icon matPrefix>search</mat-icon>
          <input matInput [(ngModel)]="availableFilter" placeholder="Search available" />
        </mat-form-field>
        <div class="column-list">
          <button mat-stroked-button type="button" *ngFor="let item of filteredAvailable" (click)="add(item)">{{ item }}</button>
        </div>
      </div>

      <div class="panel selected-panel">
        <div class="panel-header">Selected Columns</div>
        <mat-form-field appearance="outline">
          <mat-icon matPrefix>search</mat-icon>
          <input matInput [(ngModel)]="selectedFilter" placeholder="Search selected" />
        </mat-form-field>
        <div class="column-list">
          <button mat-stroked-button type="button" *ngFor="let item of filteredSelected" (click)="remove(item)">{{ item }}</button>
        </div>
      </div>
    </div>

    <div mat-dialog-actions align="end">
      <button mat-button type="button" (click)="addAll()">Add All &gt;&gt;</button>
      <button mat-button type="button" color="primary" (click)="save()">Apply</button>
    </div>
  `,
    styles: [
        '.config-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; min-width: 560px; }',
        '.panel { border: 1px solid var(--border); border-radius: 12px; padding: 0.8rem; background: #fff; }',
        '.panel-header { font-size: 12px; letter-spacing: .08em; text-transform: uppercase; color: var(--text-muted); margin-bottom: .75rem; }',
        '.column-list { display: flex; flex-wrap: wrap; gap: .5rem; min-height: 120px; }',
        '.column-list button { min-width: 120px; }',
        '@media (max-width: 600px) { .config-grid { grid-template-columns: 1fr; min-width: auto; } }'
    ]
})
export class ConfigureColumnsDialogComponent {
    available = ['ACCOUNT ID', 'RESULT', 'REASON', 'STATUS'];
    selected = ['ACCOUNT ID', 'RESULT', 'REASON'];
    availableFilter = '';
    selectedFilter = '';

    constructor(private readonly dialogRef: MatDialogRef<ConfigureColumnsDialogComponent>) { }

    get filteredAvailable() {
        return this.available.filter((item) => item.toLowerCase().includes(this.availableFilter.toLowerCase()) && !this.selected.includes(item));
    }

    get filteredSelected() {
        return this.selected.filter((item) => item.toLowerCase().includes(this.selectedFilter.toLowerCase()));
    }

    add(item: string): void {
        if (!this.selected.includes(item)) {
            this.selected = [...this.selected, item];
        }
    }

    remove(item: string): void {
        this.selected = this.selected.filter((value) => value !== item);
    }

    addAll(): void {
        this.selected = [...new Set([...this.selected, ...this.available])];
    }

    save(): void {
        this.dialogRef.close(this.selected);
    }
}
