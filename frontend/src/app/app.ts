import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

// --- Imports des "Widgets" PrimeNG ---
import { InputTextareaModule } from 'primeng/inputtextarea';
import { ButtonModule } from 'primeng/button';
import { ImageModule } from 'primeng/image';
import { SkeletonModule } from 'primeng/skeleton';
import { CardModule } from 'primeng/card';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api'; // Pour les notifications

@Component({
    selector: 'app-root',
    standalone: true,
    // On déclare les widgets qu'on va utiliser
    imports: [
        FormsModule,
        InputTextareaModule,
        ButtonModule,
        ImageModule,
        SkeletonModule,
        CardModule,
        ToastModule
    ],
    providers: [MessageService], // Service pour les popups
    templateUrl: './app.html',
    styleUrl: './app.scss'
})
export class App {
    title = 'Neuclid';
    prompt: string = '';

    imageUrl = signal<string | null>(null);
    isLoading = signal<boolean>(false);

    constructor(private http: HttpClient, private messageService: MessageService) { }

    generateFigure() {
        if (!this.prompt.trim()) return;

        this.isLoading.set(true);
        this.imageUrl.set(null);

        const payload = { prompt: this.prompt };

        this.http.post<any>('http://localhost:8000/api/v1/geometry/generate', payload)
            .subscribe({
                next: (response) => {
                    this.imageUrl.set(response.image_url);
                    this.isLoading.set(false);
                    // Petite notification sympa "Toast"
                    this.messageService.add({ severity: 'success', summary: 'Succès', detail: 'Figure générée avec succès' });
                },
                error: (error) => {
                    this.isLoading.set(false);
                    this.messageService.add({ severity: 'error', summary: 'Erreur', detail: 'Impossible de générer la figure' });
                }
            });
    }
}