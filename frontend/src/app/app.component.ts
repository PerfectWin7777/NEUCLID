import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common'; // Important pour les directives de base
import { FormsModule } from '@angular/forms';
import { SmartCanvasComponent } from './components/smart-canvas/smart-canvas.component';
import { CodeEditorComponent } from './components/code-editor/code-editor.component';

// PrimeNG Imports
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { SplitterModule } from 'primeng/splitter'; // Pour redimensionner les zones !
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { ImageModule } from 'primeng/image';
import { TabViewModule } from 'primeng/tabview';
import { TooltipModule } from 'primeng/tooltip';

import { AppService } from './core/services/app.service';

@Component({
    selector: 'app-root',
    standalone: true,
    imports: [
        CommonModule,
        TooltipModule,
        FormsModule,
        ButtonModule,
        InputTextModule,
        SplitterModule,
        ScrollPanelModule,
        ImageModule,
        TabViewModule,
        SmartCanvasComponent,
        CodeEditorComponent
        
    ],
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent {
    // On injecte notre "Cerveau"
    appService = inject(AppService);

    // Variable pour l'input (liée avec ngModel)
    userPrompt = '';

    // --- GESTION DES PANNEAUX ---
    // Taille par défaut : [Gauche(20), Centre(50), Droite(30)]
    panelSizes = signal<number[]>([20, 50, 30]);

    // Pour se souvenir de la taille avant fermeture
    lastLeftSize = 20;
    lastRightSize = 30;

    toggleLeftPanel() {
        const current = this.panelSizes();
        // Si la taille est > 1 (marge d'erreur), on considère ouvert
        if (current[0] > 1) {
            this.lastLeftSize = current[0]; // Sauvegarde
            // On ferme : [0, centre agrandi, droite inchangée]
            this.panelSizes.set([0, current[1] + current[0], current[2]]);
        } else {
            // On ouvre : [taille sauvée, centre réduit, droite inchangée]
            // Sécurité : si la taille sauvée est trop petite (ex: 0), on met 20 par défaut
            const sizeToRestore = this.lastLeftSize > 5 ? this.lastLeftSize : 20;
            const newCenter = current[1] - sizeToRestore;
            this.panelSizes.set([sizeToRestore, newCenter, current[2]]);
        }
    }

    toggleRightPanel() {
        const current = this.panelSizes();
        if (current[2] > 1) {
            this.lastRightSize = current[2];
            this.panelSizes.set([current[0], current[1] + current[2], 0]);
        } else {
            const sizeToRestore = this.lastRightSize > 5 ? this.lastRightSize : 30;
            const newCenter = current[1] - sizeToRestore;
            this.panelSizes.set([current[0], newCenter, sizeToRestore]);
        }
    }


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

    onManualCompile(code: string) {
        this.appService.compileManual(code).subscribe({
            error: (err) => console.error('Erreur compilation:', err)
        });
    }

    onFixWithAi(code: string) {
        console.log('TODO: Implémenter la réparation IA pour', code);
        // Ici on appellera plus tard un endpoint spécial
    }
}