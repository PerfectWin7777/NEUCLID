import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { mapStepToVisual, VisualStep } from './step-mapper';
import { ScrollPanelModule } from 'primeng/scrollpanel';

@Component({
    selector: 'app-construction-tree',
    standalone: true,
    imports: [CommonModule, ScrollPanelModule],
    templateUrl: './construction-tree.component.html',
    styleUrls: ['./construction-tree.component.scss']
})
export class ConstructionTreeComponent implements OnChanges {

    // L'entrée : Le JSON brut qui vient de ton backend (via AppService)
    @Input() data: any;

    // La sortie : La liste propre prête à être affichée
    visualSteps: VisualStep[] = [];

    ngOnChanges(changes: SimpleChanges) {
        if (changes['data'] && this.data) {
            // 1. On vérifie si on a bien une liste d'étapes dans le JSON
            // (Sécurité : si le JSON est vide ou mal formé, on met un tableau vide)
            const rawSteps = this.data.construction_steps || [];

            // 2. MAGIE : On transforme chaque étape brute en étape visuelle
            // grâce à ton fichier step-mapper.ts
            this.visualSteps = rawSteps.map((step: any) => mapStepToVisual(step));

            console.log('Construction Tree Generated:', this.visualSteps);
        }
    }
}