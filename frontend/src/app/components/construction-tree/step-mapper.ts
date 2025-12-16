// src/app/components/construction-tree/step-mapper.ts

// 1. Définition de ce à quoi ressemble une ligne "Visuelle"
// Le composant d'affichage ne connaitra QUE cette interface.
export interface VisualStep {
    id: string;          // L'identifiant unique (ex: "A", "c1")
    type: string;        // Le type brut (pour debug ou icône par défaut)

    // Ce qu'on affiche à l'écran
    icon: string;        // Classe de l'icône PrimeIcons (ex: 'pi pi-stop')
    iconColor: string;   // Couleur de l'icône (ex: 'text-blue-400')
    title: string;       // Gros titre (ex: "Point A")
    subtitle: string;    // Petit détail (ex: "Coords: 0, 5")

    // Pour l'interactivité future
    isDrawAction: boolean; // Est-ce une action de dessin (Draw) ou de calcul (Def) ?
}

// 2. Le Dictionnaire de traduction
// C'est ici qu'on configure l'intelligence d'affichage.
export function mapStepToVisual(step: any): VisualStep {

    // Valeurs par défaut (si le type est inconnu)
    let visual: VisualStep = {
        id: step.id || '?',
        type: step.type,
        icon: 'pi pi-cog',      // Roue dentée par défaut
        iconColor: 'text-gray-500',
        title: step.type,       // On affiche le type brut par défaut
        subtitle: '',
        isDrawAction: false
    };

    // --- LOGIQUE DE TRADUCTION PAR TYPE ---
    switch (step.type) {

        // === CAS 1 : LES POINTS ===
        case 'def_point_coords':
            visual.icon = 'pi pi-stop'; // Carré plein
            visual.iconColor = 'text-blue-400'; // Bleu
            visual.title = `Point ${step.id}`;
            // On formate les coordonnées joliment
            visual.subtitle = `(${step.coords[0]}, ${step.coords[1]})`;
            break;

        case 'def_midpoint':
            visual.icon = 'pi pi-stop';
            visual.iconColor = 'text-cyan-400'; // Cyan pour distinguer
            visual.title = `Milieu ${step.id}`;
            visual.subtitle = `de [${step.of_segment[0]}, ${step.of_segment[1]}]`;
            break;

        // === CAS 2 : LES LIGNES / SEGMENTS ===
        case 'draw_segments':
            visual.icon = 'pi pi-minus'; // Trait
            visual.iconColor = 'text-yellow-400';
            visual.isDrawAction = true;
            // On récupère les paires de points (ex: A-B)
            const segments = step.segments.map((s: any) => `[${s[0]}${s[1]}]`).join(', ');
            visual.title = 'Segments';
            visual.subtitle = segments;
            break;

        case 'draw_polygon':
            visual.icon = 'pi pi-box'; // Boite
            visual.iconColor = 'text-orange-400';
            visual.isDrawAction = true;
            visual.title = 'Polygone';
            visual.subtitle = step.point_ids.join('-');
            break;

        // === CAS 3 : LES CERCLES ===
        case 'def_circle_by_center_radius':
        case 'def_circle_by_center_point':
            visual.icon = 'pi pi-circle'; // Rond vide
            visual.iconColor = 'text-red-400';
            visual.title = `Cercle ${step.id}`;
            visual.subtitle = `Centre: ${step.center}`;
            break;

        case 'draw_circles':
            visual.icon = 'pi pi-circle-fill'; // Rond plein (action de tracer)
            visual.iconColor = 'text-red-500';
            visual.isDrawAction = true;
            visual.title = 'Tracer Cercle(s)';
            visual.subtitle = step.circle_ids.join(', ');
            break;

        // === CAS 4 : TEXTE / LABELS ===
        case 'label_points':
            visual.icon = 'pi pi-tag';
            visual.iconColor = 'text-gray-400';
            visual.isDrawAction = true;
            visual.title = 'Étiquettes';
            if (step.point_ids) {
                visual.subtitle = step.point_ids.join(', ');
            } else {
                visual.subtitle = 'Labels personnalisés';
            }
            break;
    }

    return visual;
}