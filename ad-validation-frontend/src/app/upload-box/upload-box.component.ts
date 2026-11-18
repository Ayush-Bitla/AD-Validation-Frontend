import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
    selector: 'app-upload-box',
    standalone: true,
    imports: [CommonModule, MatButtonModule, MatIconModule],
    templateUrl: './upload-box.component.html',
    styleUrls: ['./upload-box.component.css']
})
export class UploadBoxComponent {
    @Input() label = 'Upload file';
    @Input() icon = 'cloud_upload';
    @Input() file: File | null = null;
    @Input() sheet = '';
    @Input() error: string | null = null;
    @Input() valid = false;
    @Input() accepted = '.csv,.xlsx';
    @Output() fileChange = new EventEmitter<File>();
    @Output() sheetChange = new EventEmitter<string>();
    @Output() clear = new EventEmitter<void>();

    isDragging = false;

    openPicker(input: HTMLInputElement): void {
        input.click();
    }

    handleInput(event: Event): void {
        const input = event.target as HTMLInputElement;
        const selected = input.files?.[0];
        if (selected) {
            this.fileChange.emit(selected);
        }
        input.value = '';
    }

    handleDrop(event: DragEvent): void {
        event.preventDefault();
        this.isDragging = false;
        const file = event.dataTransfer?.files?.[0];
        if (file) {
            this.fileChange.emit(file);
        }
    }

    updateSheet(value: string): void {
        this.sheetChange.emit(value);
    }

    onClear(): void {
        this.clear.emit();
    }

    get fileSizeLabel(): string {
        if (!this.file) {
            return '';
        }
        const kb = this.file.size / 1024;
        return `${Math.max(1, Math.round(kb))} KB`;
    }
}
