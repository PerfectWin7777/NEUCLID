// src/app/core/models/generation.model.ts

export interface GenerationResult {
    image_url: string;      // L'URL complète pour l'affichage
    latex_code: string;     // Le code source pour l'éditeur
    json_content: any;      // Le plan de construction (pour le debug/inspecteur)
    tool_name: string;      // Pour savoir quel outil a travaillé
    metadata: {
        steps_count: number;
        model_used: string;
    };
    timestamp?: Date;       // On l'ajoutera nous-mêmes côté front pour l'historique
}

export interface GenerationRequest {
    prompt: string;
}