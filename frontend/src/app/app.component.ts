import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common'; // Important pour les directives de base
import { FormsModule } from '@angular/forms';

// PrimeNG Imports
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { SplitterModule } from 'primeng/splitter'; // Pour redimensionner les zones !
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { ImageModule } from 'primeng/image';

import { AppService } from './core/services/app.service';

@Component({
    selector: 'app-root',
    standalone: true,
    imports: [
        CommonModule,
        FormsModule,
        ButtonModule,
        InputTextModule,
        SplitterModule,
        ScrollPanelModule,
        ImageModule 
        
    ],
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent {
    // On injecte notre "Cerveau"
    appService = inject(AppService);

    // Variable pour l'input (liée avec ngModel)
    userPrompt = '';

    onGenerate() {
        if (!this.userPrompt.trim()) return;

        // On appelle le service
        this.appService.generate(this.userPrompt).subscribe({
            error: (err) => console.error('Erreur:', err)
            // Le succès est géré dans le service via le 'tap'
        });

        // On vide pas forcément l'input, question d'UX (à décider)
        // this.userPrompt = ''; 
    }
}