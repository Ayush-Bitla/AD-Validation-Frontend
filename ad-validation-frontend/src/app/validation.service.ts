import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';

import { ValidationResponse } from './models';

@Injectable({ providedIn: 'root' })
export class ValidationService {
    private readonly http = inject(HttpClient);

    runValidation(formData: FormData) {
        return this.http.post<ValidationResponse>('/api/validate', formData);
    }
}
