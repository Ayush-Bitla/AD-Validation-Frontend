import { Component } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import { ValidationPageComponent } from '../validation-page/validation-page.component';

@Component({
    selector: 'app-shell',
    standalone: true,
    imports: [MatButtonModule, MatIconModule, ValidationPageComponent],
    templateUrl: './shell.component.html',
    styleUrls: ['./shell.component.css']
})
export class ShellComponent { }
