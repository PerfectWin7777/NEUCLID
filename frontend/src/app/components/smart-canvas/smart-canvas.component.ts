import { Component, Input, Output, EventEmitter, ElementRef, ViewChild, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GenerationResult } from '../../core/models/generation.model';

@Component({
    selector: 'app-smart-canvas',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './smart-canvas.component.html',
    styleUrls: ['./smart-canvas.component.scss']
})
export class SmartCanvasComponent {
    // --- ENTRÉES (Ce que le parent nous donne) ---
    @Input() items: GenerationResult[] = []; // La liste des images (1 ou 4)
    @Input() isLoading: boolean = false;

    // --- SORTIES (Ce qu'on renvoie au parent) ---
    @Output() selectItem = new EventEmitter<GenerationResult>();

    // --- ÉTAT INTERNE (State) ---
    mode = signal<'GRID' | 'DETAIL'>('GRID'); // On commence en mode grille
    selectedImage = signal<GenerationResult | null>(null);

    // Variables pour le Zoom/Pan (Mathématiques)
    scale = 1;      // Niveau de zoom (1 = 100%)
    panning = false; // Est-ce qu'on est en train de glisser ?
    pointX = 0;     // Position X de l'image
    pointY = 0;     // Position Y de l'image
    startX = 0;     // Là où on a cliqué pour commencer à glisser
    startY = 0;

    @ViewChild('transformLayer') transformLayer!: ElementRef;

    // --- LOGIQUE DE NAVIGATION ---

    // 1. Quand on clique sur une image de la grille
    enterDetailMode(item: GenerationResult) {
        this.selectedImage.set(item);
        this.mode.set('DETAIL');
        this.resetView(); // On remet le zoom à zéro
        this.selectItem.emit(item); // On prévient le parent (pour mettre à jour l'inspecteur à droite)
    }

    // 2. Retour à la grille
    backToGrid() {
        this.mode.set('GRID');
        this.selectedImage.set(null);
    }

    // 3. Reset du zoom (Double clic ou bouton)
    resetView() {
        this.scale = 1;
        this.pointX = 0;
        this.pointY = 0;
        this.updateTransform();
    }

    // --- MOTEUR PHYSIQUE (Zoom & Pan) ---

    onWheel(event: WheelEvent) {
        if (this.mode() !== 'DETAIL') return; // Pas de zoom en mode grille
        event.preventDefault(); // Empêche de scroller la page

        const xs = (event.clientX - this.pointX) / this.scale;
        const ys = (event.clientY - this.pointY) / this.scale;
        const delta = event.deltaY < 0 ? 1.1 : 0.9; // Zoom in ou out

        // On applique le zoom
        this.scale *= delta;

        // Limites (Min 10%, Max 500%)
        if (this.scale < 0.1) this.scale = 0.1;
        if (this.scale > 5) this.scale = 5;

        // On ajuste la position pour zoomer vers le curseur (Maths vectorielles)
        this.pointX = event.clientX - xs * this.scale;
        this.pointY = event.clientY - ys * this.scale;

        this.updateTransform();
    }

    startPan(event: MouseEvent) {
        if (this.mode() !== 'DETAIL') return;
        this.panning = true;
        this.startX = event.clientX - this.pointX;
        this.startY = event.clientY - this.pointY;
    }

    doPan(event: MouseEvent) {
        if (!this.panning) return;
        event.preventDefault();
        this.pointX = event.clientX - this.startX;
        this.pointY = event.clientY - this.startY;
        this.updateTransform();
    }

    endPan() {
        this.panning = false;
    }

    // Applique les calculs au CSS
    updateTransform() {
        if (!this.transformLayer) return;
        const el = this.transformLayer.nativeElement;
        // C'est ici la magie GPU : translate3d est accéléré par la carte graphique
        el.style.transform = `translate3d(${this.pointX}px, ${this.pointY}px, 0px) scale(${this.scale})`;
    }
}