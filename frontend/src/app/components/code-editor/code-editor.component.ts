import { Component, ElementRef, Input, Output, ViewChild, EventEmitter, OnChanges, AfterViewInit, SimpleChanges, OnDestroy, ViewEncapsulation } from '@angular/core';
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
import { stex } from '@codemirror/legacy-modes/mode/stex';

@Component({
    selector: 'app-code-editor',
    standalone: true,
    imports: [CommonModule, ButtonModule, TooltipModule],
    templateUrl: './code-editor.component.html',
    styleUrls: ['./code-editor.component.scss'],
    encapsulation: ViewEncapsulation.None // IMPORTANT pour que le CSS ::ng-deep fonctionne bien
})
export class CodeEditorComponent implements AfterViewInit, OnChanges, OnDestroy {

    @Input() code: string = '';
    @Input() isCompiling: boolean = false;
    @Output() onRecompile = new EventEmitter<string>();
    @Output() onRequestFix = new EventEmitter<string>();

    @ViewChild('editorContainer') editorContainer!: ElementRef;

    private editor!: EditorView;
    isCopied = false;

    ngAfterViewInit() {
        // On attend un micro-tick pour être sûr que le DOM est prêt
        setTimeout(() => {
            this.initEditor();
        }, 0);
    }

    ngOnChanges(changes: SimpleChanges) {
        // Si le code change depuis le parent (ex: clic sur une autre image)
        if (changes['code'] && this.editor) {
            const newValue = changes['code'].currentValue || '';
            const currentValue = this.editor.state.doc.toString();

            if (newValue !== currentValue) {
                this.editor.dispatch({
                    changes: { from: 0, to: currentValue.length, insert: newValue }
                });
            }
        }
    }

    private initEditor() {
        if (!this.editorContainer) {
            console.error('Editor Container not found!');
            return;
        }

        // Configuration initiale
        const startState = EditorState.create({
            doc: this.code, // On injecte le code initial ici
            extensions: [
                basicSetup,
                keymap.of([indentWithTab]),
                oneDark, // Thème sombre indispensable
                StreamLanguage.define(stex), // Mode LaTeX
                EditorView.lineWrapping, // Retour à la ligne automatique

                // Raccourci Ctrl+Enter
                keymap.of([{
                    key: 'Mod-Enter',
                    run: () => {
                        this.triggerCompile();
                        return true;
                    }
                }]),
            ]
        });

        this.editor = new EditorView({
            state: startState,
            parent: this.editorContainer.nativeElement
        });

        console.log('CodeMirror initialized with code length:', this.code.length);
    }

    triggerCompile() {
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
            setTimeout(() => this.isCopied = false, 2000);
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