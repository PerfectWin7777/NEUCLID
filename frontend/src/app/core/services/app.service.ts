import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { GenerationResult, GenerationRequest } from '../models/generation.model';
import { tap } from 'rxjs/operators';

@Injectable({
    providedIn: 'root' // Dispo partout dans l'app (Singleton)
})
export class AppService {
    private apiUrl = 'http://localhost:8000/api/v1/generate';

    // --- ÉTAT (STATE) ---
    // C'est la mémoire vive de ton application.

    // 1. L'historique complet des générations
    // WritableSignal = Une variable qu'on peut modifier et qui met à jour l'UI toute seule
    history = signal<GenerationResult[]>([]);

    // 2. L'élément actuellement sélectionné (celui qu'on affiche au centre)
    currentSelection = signal<GenerationResult | null>(null);

    // 3. Est-ce qu'on est en train de charger ?
    isLoading = signal<boolean>(false);

    constructor(private http: HttpClient) { }

    // --- ACTIONS ---

    generate(prompt: string) {
        this.isLoading.set(true); // On active le spinner

        const payload: GenerationRequest = { prompt };

        return this.http.post<GenerationResult>(this.apiUrl, payload).pipe(
            tap((result) => {
                // Cette fonction s'exécute quand le backend répond SUCCÈS

                // 1. On ajoute le timestamp
                result.timestamp = new Date();

                // 2. On met à jour l'historique (On ajoute le nouveau au début de la liste)
                this.history.update(list => [result, ...list]);

                // 3. On sélectionne automatiquement le nouveau résultat
                this.currentSelection.set(result);

                this.isLoading.set(false); // On coupe le spinner
            })
        );
    }
    
    // méthode pour la compilation manuelle
    compileManual(latexCode: string) {
        this.isLoading.set(true);

        const payload = { latex_code: latexCode };
        const compileUrl = 'http://localhost:8000/api/v1/compile'; // La route backend qu'on a créée

        return this.http.post<any>(compileUrl, payload).pipe(
            tap((response) => {
                // La réponse contient { image_url: '...' }
                // On doit mettre à jour l'élément actuel avec la nouvelle image
                const current = this.currentSelection();

                if (current) {
                    // On crée une copie mise à jour (Immutabilité pour les Signals)
                    const updated = { ...current, image_url: response.image_url, latex_code: latexCode };

                    // On met à jour la sélection ET l'historique
                    this.currentSelection.set(updated);

                    // (Optionnel) Mise à jour dans l'historique aussi pour garder la cohérence
                    this.history.update(list => list.map(item => item === current ? updated : item));
                }

                this.isLoading.set(false);
            })
        );
    }

    // Action pour sélectionner une image dans l'historique
    selectItem(item: GenerationResult) {
        this.currentSelection.set(item);
    }
}