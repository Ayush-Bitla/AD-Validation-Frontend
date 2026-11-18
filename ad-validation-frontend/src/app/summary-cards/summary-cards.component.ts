import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';

interface SummaryCard {
    label: string;
    value: number;
    icon: string;
    tone: string;
}

@Component({
    selector: 'app-summary-cards',
    standalone: true,
    imports: [CommonModule, MatIconModule],
    templateUrl: './summary-cards.component.html',
    styleUrls: ['./summary-cards.component.css']
})
export class SummaryCardsComponent {
    @Input() totalAccounts = 0;
    @Input() dc = 0;
    @Input() name = 0;
    @Input() inactive = 0;
    @Input() lastLogin = 0;
    @Input() azure = 0;

    trackByCard(index: number, card: SummaryCard): string {
        return `${card.label}-${index}`;
    }

    get cards(): SummaryCard[] {
        return [
            { label: 'Total accounts', value: this.totalAccounts, icon: 'people', tone: 'navy' },
            { label: '11 DC fails', value: this.dc, icon: 'lan', tone: 'warning' },
            { label: 'Name mismatch', value: this.name, icon: 'compare_arrows', tone: 'success' },
            { label: 'Should disable', value: this.inactive, icon: 'warning', tone: 'danger' },
            { label: 'Login 30+ days', value: this.lastLogin, icon: 'history', tone: 'info' },
            { label: 'Not in Azure', value: this.azure, icon: 'cloud_off', tone: 'purple' }
        ];
    }
}
