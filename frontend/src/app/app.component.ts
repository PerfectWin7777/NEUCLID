import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common'; // Important pour les directives de base
import { FormsModule } from '@angular/forms';
import { SmartCanvasComponent } from './components/smart-canvas/smart-canvas.component';
import { CodeEditorComponent } from './components/code-editor/code-editor.component';
import { ConstructionTreeComponent } from './components/construction-tree/construction-tree.component';

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
        CodeEditorComponent,
        ConstructionTreeComponent
        
    ],
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent {
    // On injecte notre "Cerveau"
    appService = inject(AppService);

    // Variable pour l'input (liée avec ngModel)
    userPrompt = '';

    // État initial
    panelSizes = signal<number[]>([20, 60, 20]);

    // Mémoire
    lastLeft = 20;
    lastRight = 20;

    get isLeftVisible() { return this.panelSizes()[0] > 0.5; }
    get isRightVisible() { return this.panelSizes()[2] > 0.5; }

    toggleLeftPanel() {
        const current = this.panelSizes();
        let newLeft = 0;
        let newRight = current[2];

        if (this.isLeftVisible) {
            // ON FERME
            this.lastLeft = current[0];
            newLeft = 0;
        } else {
            // ON OUVRE
            newLeft = this.lastLeft || 20;
            // Sécurité : si gauche + droite > 90%, on réduit la droite pour laisser de la place
            if (newLeft + newRight > 90) {
                newRight = 100 - newLeft - 10; // On laisse 10% au centre mini
            }
        }

        // LE SECRET EST ICI : Le centre est le reste.
        const newCenter = 100 - newLeft - newRight;
        this.panelSizes.set([newLeft, newCenter, newRight]);
    }

    toggleRightPanel() {
        const current = this.panelSizes();
        let newLeft = current[0];
        let newRight = 0;

        if (this.isRightVisible) {
            // ON FERME
            this.lastRight = current[2];
            newRight = 0;
        } else {
            // ON OUVRE
            newRight = this.lastRight || 20;
            if (newRight + newLeft > 90) {
                newLeft = 100 - newRight - 10;
            }
        }

        // LE SECRET EST ICI
        const newCenter = 100 - newLeft - newRight;
        this.panelSizes.set([newLeft, newCenter, newRight]);
    }

    onSplitterResize(event: any) {
        // Même ici, on force le recalcul pour éviter les décimales foireuses
        const [l, c, r] = event.sizes;
        // On ne stocke que si c'est "ouvert" (taille significative)
        if (l > 1) this.lastLeft = l;
        if (r > 1) this.lastRight = r;

        this.panelSizes.set(event.sizes);
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