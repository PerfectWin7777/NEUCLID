import { Component, ElementRef, Input, Output, ViewChild, EventEmitter, OnChanges, AfterViewInit, SimpleChanges, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { TooltipModule } from 'primeng/tooltip';

// --- CODEMIRROR IMPORTS ---
import { basicSetup } from 'codemirror';
import { EditorState } from '@codemirror/state';
import { EditorView, keymap, ViewUpdate } from '@codemirror/view';
import { indentWithTab } from '@codemirror/commands';
import { oneDark } from '@codemirror/theme-one-dark';
import { StreamLanguage } from '@codemirror/language';
import { stex } from '@codemirror/legacy-modes/mode/stex'; // Le mode LaTeX

@Component({
    selector: 'app-code-editor',
    standalone: true,
    imports: [CommonModule, ButtonModule, TooltipModule],
    templateUrl: './code-editor.component.html',
    styleUrls: ['./code-editor.component.scss']
})
export class CodeEditorComponent implements AfterViewInit, OnChanges, OnDestroy {

    // --- INPUTS / OUTPUTS ---
    @Input() code: string = ''; // Le code initial venant du backend
    @Input() isCompiling: boolean = false; // Pour afficher le spinner sur le bouton Play

    @Output() onRecompile = new EventEmitter<string>(); // Quand l'user clique sur Play
    @Output() onRequestFix = new EventEmitter<string>(); // Pour le bouton "Fix AI"

    // Référence au <div #editor> dans le HTML
    @ViewChild('editorContainer') editorContainer!: ElementRef;

    private editor!: EditorView;
    isCopied = false; // Pour le feedback visuel du bouton copier

    ngAfterViewInit() {
        // Initialisation de CodeMirror
        this.initEditor();
    }

    ngOnChanges(changes: SimpleChanges) {
        // Si le code change depuis le parent (ex: on a sélectionné une autre image), 
        // on met à jour l'éditeur sans casser l'historique
        if (changes['code'] && this.editor && !changes['code'].firstChange) {
            const newValue = changes['code'].currentValue;
            const currentValue = this.editor.state.doc.toString();

            // On ne met à jour que si c'est différent pour éviter les boucles
            if (newValue !== currentValue) {
                this.editor.dispatch({
                    changes: { from: 0, to: currentValue.length, insert: newValue }
                });
            }
        }
    }

    private initEditor() {
        if (!this.editorContainer) return;

        // Configuration des extensions CodeMirror
        const extensions = [
            basicSetup, // Numéros de ligne, highlight active line, brackets...
            keymap.of([indentWithTab]), // Tabulation
            oneDark, // Thème sombre VS Code style
            StreamLanguage.define(stex), // Coloration Syntaxique LaTeX

            // Raccourci Clavier : Ctrl + Enter pour recompiler
            keymap.of([{
                key: 'Mod-Enter',
                run: () => {
                    this.triggerCompile();
                    return true;
                }
            }]),

            // Listener pour détecter les changements (optionnel si on veut l'autosave)
            EditorView.updateListener.of((update: ViewUpdate) => {
                if (update.docChanged) {
                    // On pourrait émettre un event 'onChange' ici
                }
            })
        ];

        // Création de l'instance
        this.editor = new EditorView({
            state: EditorState.create({
                doc: this.code,
                extensions: extensions
            }),
            parent: this.editorContainer.nativeElement
        });
    }

    // --- ACTIONS UTILISATEUR ---

    triggerCompile() {
        // Récupère le code actuel de l'éditeur
        const currentCode = this.editor.state.doc.toString();
        this.onRecompile.emit(currentCode);
    }

    triggerFixAi() {
        const currentCode = this.editor.state.doc.toString();
        this.onRequestFix.emit(currentCode);
    }

    copyCode() {
        const currentCode = this.editor.state.doc.toString();
        navigator.clipboard.writeText(currentCode).then(() => {
            this.isCopied = true;
            setTimeout(() => this.isCopied = false, 2000); // Feedback temporaire
        });
    }

    downloadCode() {
        const currentCode = this.editor.state.doc.toString();
        const blob = new Blob([currentCode], { type: 'text/x-tex' });
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = 'figure_neuclid.tex';
        a.click();

        window.URL.revokeObjectURL(url);
    }

    ngOnDestroy() {
        if (this.editor) {
            this.editor.destroy();
        }
    }
}