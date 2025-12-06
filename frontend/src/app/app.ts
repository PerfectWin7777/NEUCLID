import { Component, signal } from '@angular/core'; // <--- On importe signal
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

@Component({
    selector: 'app-root',
    standalone: true,
    imports: [FormsModule],
    templateUrl: './app.html',
    styleUrl: './app.scss'
})
export class App {
    title = 'Neuclid';

    // Pour le champ texte, on garde une variable simple (c'est géré par ngModel)
    prompt: string = '';

    // --- LES SIGNAUX (Réactivité immédiate) ---
    // On définit des "boîtes réactives" au lieu de variables simples
    imageUrl = signal<string | null>(null);
    isLoading = signal<boolean>(false);
    errorMessage = signal<string | null>(null);

    constructor(private http: HttpClient) { }

    generateFigure() {
        if (!this.prompt.trim()) return;

        // Mise à jour des signaux : on utilise .set()
        this.isLoading.set(true);
        this.errorMessage.set(null);
        this.imageUrl.set(null);

        const payload = { prompt: this.prompt };

        this.http.post<any>('http://localhost:8000/api/v1/geometry/generate', payload)
            .subscribe({
                next: (response) => {
                    console.log('⚡ Signal reçu, mise à jour UI...');
                    // Dès qu'on fait ça, l'écran change TOUT DE SUITE
                    this.imageUrl.set(response.image_url);
                    this.isLoading.set(false);
                },
                error: (error) => {
                    console.error('❌ Erreur:', error);
                    this.errorMessage.set("Erreur de communication avec le backend.");
                    this.isLoading.set(false);
                }
            });
    }
}