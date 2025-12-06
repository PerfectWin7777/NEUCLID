# backend/src/features/geometry/translator.py

import dis
import logging
from pathlib import Path
from typing import Dict, Any,Tuple,Optional,List

# --- Nos importations locales ---
from .models import (
    Geometry2DInput, Style,
    DefinePointByCoords, 
    DefineMidPoint,
    DefineLineByPoints, 
    DefineMediator,
    DrawSegments,
    MarkSegments,
    DrawVector, 
    DrawVectorByLength,
    DrawLines, 
    DrawPoints, 
    DefineRegularPolygon,
    CalculateLength,
    LabelPoints,
    LabelSegment,
    LabelLine,
    LabelCircle,
    LabelArc,
    LabelStyle,
    MarkRightAngle,
    DefineProjectionPoint,
    DefineParallelLine,
    DefinePerpendicularLine,
    DrawPolygon,
    DefineCircleByCenterPoint,
    DefineCircleByCenterRadius,
    DefineCircleByDiameter,
    DefineCircleCircumscribed,
    DefineCircleInscribed,
    DrawCircles,
    CircleDefForIntersection,
    FindIntersectionLineLine,
    FindIntersectionLineCircle,
    FindIntersectionCircleCircle,
    DefineTangentAtPointOnCircle,
    DefineTangentsFromPointToCircle,
    DrawEllipse,
    DrawSemiCircles,
    DrawArcByPoints,
    DrawArcByAngles,
    DefinePointOnLine,
    DefinePointOnCircle,
    DrawAngle,
    CalculateAngleByPoints,
    CalculateAngleOfSlope,
    MarkAngle,
    MarkInternalAngle,
    DefineAngleBisector,
    DrawText,
    DrawAngularSectorByPoints,
    DrawAngularSectorByRotation,
    DrawAngularSectorByAngles,
    DrawAngularSectorByNodes,
    DefineTriangleBy2Points,
    DefineTriangleCenter,
    DefineSquare,
    DefineRectangle,
    DefineParallelogram,
    DefinePointsByTranslation,
    DefinePointsByHomothety,
    DefinePointsByReflection,
    DefinePointsBySymmetry,
    DefinePointsByRotation,
    FillShapeWithPattern,
    DefinePerspectiveCuboid
)

# Le compilateur LaTeX
from src.core.latex import compile_latex_to_image

log = logging.getLogger(__name__)

# ==============================================================================
#                      LA CLASSE DU TRADUCTEUR GÉOMÉTRIQUE
# ==============================================================================
class TkzEuclideTranslator:
    """
    Traduit un objet Geometry2DInput sémantique et validé en un code LaTeX
    robuste utilisant le package tkz-euclide.
    """
    def __init__(self, input_data: Geometry2DInput, show_axes: bool, show_grid: bool):
        self.data = input_data
        self.show_axes = show_axes
        self.show_grid = show_grid
        self.latex_parts = []
        self.defined_lines = {}
        self.defined_circles = {} # NOTRE  MEMOIRE INTERNE POUR STOCKER LES DEFS DES CERCLES
        self.defined_calculations = {}
        # Elle stockera la "recette de construction" de chaque point.
        self.point_construction_methods = {}

    def translate(self) -> str:
        """Méthode principale qui orchestre la traduction."""
        self._build_header()
        self._execute_construction_steps()
        self._build_footer()
        return "\n".join(self.latex_parts)
    
    #======================================================================================================
    # helper methods
    #==============================================================================================
    def _sanitize_id(self, raw_id: str) -> str:# todo: utiliser ce helper
        """Nettoie un ID pour qu'il soit sûr à utiliser en LaTeX."""
        # Remplace les caractères potentiellement dangereux par rien
        # On pourrait être plus intelligent, mais c'est robuste.
        return raw_id.replace('_', '').replace('-', '')
    
    # def _find_line_def_step(self, line_id: str) -> Any:
    #     step = next((s for s in self.data.construction_steps if 'id' in s.__dict__ and s.id == line_id), None)
    #     if not step: log.error(f"Impossible de trouver la définition de la ligne ID '{line_id}'")
    #     return step
    
    def _style_to_str(self, style: Style) -> str:
        """Convertit un objet Style en une chaîne d'options."""
        parts = [style.color]
        if style.thickness: parts.append(style.thickness)
        if style.pattern: parts.append(style.pattern)
        return f"[{', '.join(filter(None, parts))}]" if any(parts) else ""
    
    def _find_line_def_step(self, line_id: str):
        """
        Retrouve une étape de construction complète à partir de son ID.
        C'est crucial pour le dessin car cela nous donne accès à toutes
        les informations de l'étape de définition (comme le through_point).
        """
        for step in self.data.construction_steps:
            # On vérifie si l'étape a un attribut 'id' et s'il correspond
            if hasattr(step, 'id') and step.id == line_id:
                return step
        return None
    
    def _find_line_ref_points(self, line_id: str) -> Tuple[str, str]:
        step = self._find_line_def_step(line_id)
        if step and hasattr(step, 'through'): return step.through
        return None
    
    def _build_label_options(self, style: "LabelStyle") -> str:
        """Construit la chaîne d'options [...] pour les labels."""
        options = []
        if style.position: options.append(style.position)
        if style.pos is not None: options.append(f"pos={style.pos}")
        if style.swap: options.append("swap")
        if style.color: options.append(style.color)
        
        return f"[{','.join(options)}]" if options else ""
    

    def _format_circle_inter_arg(self, circle_def: "CircleDefForIntersection", name_hint: str) -> str:
        r"""
        [HELPER] Formate l'argument d'un cercle pour une commande d'intersection.
        Gère les cas 'centre/point' et 'centre/rayon'.
        Pour le cas 'rayon', il a le effet de bord d'ajouter une commande \edef
        à la liste des parties LaTeX.
        Retourne la description textuelle d'un cercle,
        mise en forme dans une paire de parenthèses, prête à l'emploi.
        Exemple de retour: "(O,A)" ou "(C,\\cRadius)"
        """
        content = ""
        if circle_def.by_center_point:
            center, point = circle_def.by_center_point
            content = f"{center},{point}"
        
        if circle_def.by_center_radius:
            center, radius_val = circle_def.by_center_radius
            # On crée un nom unique pour la macro de rayon pour éviter les collisions
            radius_macro_name = f"\\radFor{name_hint}"
            self.latex_parts.append(f"    \\edef{radius_macro_name}{{{radius_val}}}")
            content = f"{center},{radius_macro_name}"
        
        # Ce cas ne devrait jamais arriver grâce au validateur Pydantic, mais c'est une sécurité.content = ""
        return f"({content})"
    
    def _get_coords_by_id(self, point_id: str) -> Optional[Tuple[float, float]]:
        """Helper pour retrouver les coordonnées d'un point déjà défini."""
        for step in self.data.construction_steps:
            if hasattr(step, 'id') and step.id == point_id:
                if hasattr(step, 'coords'):
                    return step.coords
        return None # Devrait être trouvé par le validateur, mais sécurité

    def _build_drawing_options(self, style: Optional["Style"], base_options: List[str] = None) -> str:
        """Construit la chaîne d'options [...] pour les commandes de DESSIN."""
        # Note : C'est une version améliorée de notre ancien _style_to_str, vous pourrez l'utiliser pour les polygones aussi !
        options = base_options or []
        if style.color: options.append(style.color)
        if style.thickness: options.append(style.thickness)
        if style.pattern: options.append(style.pattern)
        if style.fill_color: options.append(f"fill={style.fill_color}")
        if style.opacity is not None: options.append(f"opacity={style.opacity}")

        return f"[{','.join(options)}]" if options else ""
    
    #======================================================================================================
    # debut des configurations
    #==============================================================================================

    def _build_header(self):
        """Construit le début de l'environnement LaTeX pour la géométrie."""
        cfg = self.data.figure_config
        self.latex_parts.extend([
            r"\begin{tikzpicture}",
            f"\\tkzInit[xmin={cfg.x_range[0]}, xmax={cfg.x_range[1]}, ymin={cfg.y_range[0]}, ymax={cfg.y_range[1]}]"
        ])

        # Utilisation des flags au cas où il passe le true/json et non True/python!   
        # Si la valeur du système (`self.show_grid`) OU la valeur de l'IA (`cfg.grid`) est `True`
        if self.show_grid or cfg.grid:
           self.latex_parts.append(r"\tkzGrid")
        if self.show_axes or cfg.axes:
           self.latex_parts.append(r"\tkzDrawX \tkzDrawY")

    def _build_footer(self):
        """Construit la fin de l'environnement LaTeX."""
        self.latex_parts.append(r"\end{tikzpicture}")

    def _execute_construction_steps(self):
        """Boucle sur les étapes et appelle la méthode de traduction correspondante."""
        for step in self.data.construction_steps:
            translator_method = getattr(self, f"_translate_{step.type}", self._translate_unknown)
            translator_method(step)
    
    def _translate_unknown(self, step: Any):
        log.warning(f"Action de construction non reconnue ou non implémentée : '{step.type}'")
        self.latex_parts.append(f"% Action '{step.type}' ignorée.")


    #======================================================================================================
    # les traducteurs en actions
    #==============================================================================================


    # --- MÉTHODES DE TRADUCTION POUR CHAQUE TYPE D'ACTION ---

    def _translate_def_point_coords(self, step: "DefinePointByCoords"):
        self.latex_parts.append(f"    \\tkzDefPoint({step.coords[0]},{step.coords[1]}){{{step.id}}}")
        # On enregistre sa "recette" dans notre nouvelle mémoire
        self.point_construction_methods[step.id] = {
            'type': 'coords',
            'value': step.coords
        }

    # def _translate_def_point_coords(self, step: "DefinePointByCoords"):
    #     safe_id = self._sanitize_id(step.id)
    #     self.latex_parts.append(f"    \\tkzDefPoint({step.coords[0]},{step.coords[1]}){{{safe_id}}}")

    def _translate_def_midpoint(self, step: "DefineMidPoint"):
        p1, p2 = step.of_segment
        self.latex_parts.append(f"    \\tkzDefMidPoint({p1},{p2}){{{step.id}}}")
        self.latex_parts.append(f"    \\tkzGetPoint{{{step.id}}}")


    def _translate_def_line_by_points(self, step: "DefineLineByPoints"):
        r"""
        Traduit la DÉCLARATION d'une ligne par deux points connus.
        ACTION: Ne génère aucun LaTeX. Mémorise simplement la paire de points
        associée à l'ID de la ligne pour le dessin futur.
        """
        self.defined_lines[step.id] = step.through
        
    def _translate_def_parallel_line(self, step: "DefineParallelLine"):
        r"""Traduit la définition d'une ligne parallèle."""
        p_ref1, p_ref2 = step.to_line_from_points
        # 1. Nomme les deux points calculés de cette nouvelle ligne pour la rendre dessinable.
        # On crée un NOUVEAU point qui a le MÊME nom que l'ID de la ligne. C'est notre convention.
        self.latex_parts.append(
            f"    \\tkzDefLine[parallel=through {step.through_point}]({p_ref1},{p_ref2}) \\tkzGetPoint{{{step.id}}}"
        )
        # La leçon apprise : on mémorise le `through_point` et le nouveau point calculé.
        self.defined_lines[step.id] = (step.through_point, step.id)

    def _translate_def_perpendicular_line(self, step: "DefinePerpendicularLine"):
        r"""Traduit la définition d'une ligne perpendiculaire."""
        p_ref1, p_ref2 = step.to_line_from_points
        # 1. La logique de nommage des points est rigoureuse.
        self.latex_parts.append(
            f"    \\tkzDefLine[orthogonal=through {step.through_point}]({p_ref1},{p_ref2}) \\tkzGetPoint{{{step.id}}}"
        )
        # On mémorise la même paire logique : le point connu et le point calculé.
        self.defined_lines[step.id] = (step.through_point, step.id)

    def _translate_def_mediator(self, step: "DefineMediator"):
        r"""CALCULE une médiatrice et MÉMORISE les deux nouveaux points calculés."""
        p1, p2 = step.of_segment
        
        # On crée des noms uniques pour les deux points de bordure qui seront créés.
        start_point_name = f"{step.id}_A"
        end_point_name = f"{step.id}_B"

        # On calcule la médiatrice et on récupère ses extrémités avec \tkzGetPoints.
        self.latex_parts.append(f"    \\tkzDefLine[mediator]({p1},{p2})")
        self.latex_parts.append(f"    \\tkzGetPoints{{{start_point_name}}}{{{end_point_name}}}")

        # On mémorise ces deux nouveaux points, qui serviront au dessin.
        self.defined_lines[step.id] = (start_point_name, end_point_name)

    def _translate_draw_polygon(self, step: "DrawPolygon"):
        style = self._style_to_str(step.style)
        points = ",".join(step.point_ids)
        self.latex_parts.append(f"    \\tkzDrawPolygon{style}({points})")
    
    def _translate_def_regular_polygon(self, step: "DefineRegularPolygon"):
        r"""Traduit la définition des points d'un polygone régulier."""
        p1, p2 = step.from_points
        # On utilise le `build_method` et le bon nom de paramètre `sides`.
        # On construit la bonne liste d'options, avec 'name'.
        options_str = f"[{step.build_method},sides={step.num_sides},name={step.name_prefix}]"
        
        self.latex_parts.append(f"    \\tkzDefRegPolygon{options_str}({p1},{p2})")
        
        
    def _translate_draw_segments(self, step: "DrawSegments"):
        """Dessine une liste de segments individuels."""
        # On commence avec les options de base (flèches).
        base_options = []
        if step.arrow_spec:
            base_options.append(step.arrow_spec)
        options_str = self._build_drawing_options(step.style, base_options=base_options)
        # On transforme [["A","B"], ["B","C"]] en ["A,B", "B,C"]
        point_pairs = [f"{p1},{p2}" for p1, p2 in step.segments]
        # On les joint avec un ESPACE, pas une virgule, pour obtenir "A,B B,C".
        segments_str = " ".join(point_pairs)
        self.latex_parts.append(f"    \\tkzDrawSegments{options_str}({segments_str})")
    

    def _translate_draw_lines(self, step: "DrawLines"):
        r"""
        Dessine des lignes en utilisant les paires de points (p1, p2) stockées dans la mémoire
        interne (self.defined_lines), quelle que soit la manière dont elles ont été définies.
        Elle boucle sur
        chaque ID de ligne et utilise la commande \\tkzDrawLine (au singulier)
        pour chaque ligne, ce qui est plus stable.
        Elle ignore l'action si la liste des lignes est vide.
        """
        # 1. Le garde-fou. Si pas de lignes, on ne fait rien.
        if not step.line_ids:
            return
        
        options_str = self._build_drawing_options(step.style)
        
        for line_id in step.line_ids:
            # On cherche d'abord dans notre mémoire de lignes déclarées.
            if line_id in self.defined_lines:
                # On récupère la bonne paire de points (ex: ('A','B') ou ('perpP_A','perpP_B'))
                p1, p2 = self.defined_lines[line_id]
                self.latex_parts.append(f"    \\tkzDrawLine{options_str}({p1},{p2})")
            
            # (Note: la partie avec la recherche def_step pour les perp. n'est plus utile,
            # car elles seront aussi mémorisées. Mais gardons ça simple pour l'instant.)
            else:
                log.warning(f"Impossible de dessiner la ligne ID '{line_id}', sa définition est introuvable.")
    
    def _translate_draw_points(self, step: "DrawPoints"):
        style = self._style_to_str(step.style)
        self.latex_parts.append(f"    \\tkzDrawPoints{style}({','.join(step.point_ids)})")
    
    def _translate_draw_vector(self, step: "DrawVector"):
        r"""Traduit le dessin d'un vecteur.
        Cette méthode est un "alias intelligent" qui prépare les données et
        appelle le traducteur de segments.
        """
        # On crée un faux 'step' de type DrawSegments pour le passer à l'autre traducteur.
        # C'est une manière très propre de réutiliser notre code existant.
        temp_draw_segment_step = DrawSegments(
            segments=[[step.start_point_id, step.end_point_id]],
            arrow_spec="->", # On force la spécification de la flèche
            style=step.style
        )
        self._translate_draw_segments(temp_draw_segment_step)
    
    def _translate_draw_vector_by_length(self, step: "DrawVectorByLength"):
        r"""Traduit le dessin d'un vecteur par longueur et direction.
        Automatise un processus en 3 étapes : calcul de longueur, définition de
        point, et dessin de segment fléché.
        """
        # 1. Préparer les noms des macros et points intermédiaires
        len_macro_name = f"len{step.start_point_id}{step.direction_point_id}"
        new_endpoint_name = f"{step.start_point_id}vecEnd"

        # 2. Étape de calcul LaTeX : longueur du segment de direction
        self.latex_parts.append(
            f"    \\tkzCalcLength({step.start_point_id},{step.direction_point_id})\\tkzGetLength{{{len_macro_name}}}"
        )

        # 3. Étape de calcul LaTeX : définition du nouveau point final
        # On calcule la position relative : longueur_voulue / longueur_réelle
        pos_str = f"{{{step.length}/\\{len_macro_name}}}"
        self.latex_parts.append(
            f"    \\tkzDefPointOnLine[pos={pos_str}]({step.start_point_id},{step.direction_point_id}) \\tkzGetPoint{{{new_endpoint_name}}}"
        )
        
        # 4. Étape de dessin : utiliser notre traducteur de segments
        # en construisant un "faux step" à la volée.
        temp_step = DrawSegments(
            segments=[(step.start_point_id, new_endpoint_name)],
            arrow_spec="->",
            style=step.style
        )
        self._translate_draw_segments(temp_step)


    def _translate_label_points(self, step: "LabelPoints"):
        """
        Traduit la labellisation des points en s'adaptant au mode choisi (simple ou personnalisé).
        """
        style_options = self._style_to_str(step.style)
        
        # CAS 1 : Mode simple avec placement automatique
        if step.point_ids:
            ids_str = ",".join(step.point_ids)
            self.latex_parts.append(f"    \\tkzLabelPoints{style_options}({ids_str})")

        # CAS 2 : Mode personnalisé avec placement contrôlé
        elif step.custom_labels:
            for point_id, label_details in step.custom_labels.items():
                
                # --- A. Construire la liste des options [option1,option2,...] ---
                options = [label_details.position] # La position est la base.
                
                # Appliquer le style : style du label si présent, sinon style global.
                style_to_apply = label_details.style or step.style
                if style_to_apply:
                    if style_to_apply.color: options.append(style_to_apply.color)
                    if style_to_apply.thickness: options.append(style_to_apply.thickness)
                    # Le "pattern" n'est pas pertinent pour du texte, on l'ignore.
                
                options_str = f"[{','.join(options)}]" if options else ""

                # --- B. Déterminer le texte du label {texte} ---
                # Si le texte n'est pas fourni, on utilise l'ID du point par défaut.
                label_text = label_details.text or point_id
                text_str = f"{{${label_text}$}}"
                
                # --- C. Assembler la commande finale ---
                self.latex_parts.append(f"    \\tkzLabelPoint{options_str}({point_id}){text_str}")

    def _translate_label_segment(self, step: "LabelSegment"):
        options_str = self._build_label_options(step.style)
        points_str = ",".join(step.on_segment)
        label_text = f"{{${step.text}$}}"
        self.latex_parts.append(f"    \\tkzLabelSegment{options_str}({points_str}){label_text}")

    def _translate_label_line(self, step: "LabelLine"):
        options_str = self._build_label_options(step.style)
        points_str = ",".join(step.on_line)
        label_text = f"{{${step.text}$}}"
        self.latex_parts.append(f"    \\tkzLabelLine{options_str}({points_str}){label_text}")
    
    def _translate_mark_segments(self, step: "MarkSegments"):
        r"""Traduit l'action de dessiner des marques sur des segments."""
        # 1. Construction des options de style
        style_options = []
        # Le type de marque est obligatoire, pas de `if`
        style_options.append(f"mark={step.style.mark_type}")
        
        if step.style.pos is not None:
            style_options.append(f"pos={step.style.pos}")
        if step.style.color:
            style_options.append(f"color={step.style.color}")
        if step.style.size:
            style_options.append(f"size={step.style.size}")
            
        options_str = f"[{','.join(style_options)}]" if style_options else ""

        # 2. Construction de la liste des segments
        # La doc de LaTeX est claire : les paires sont séparées par un espace.
        segments_str = " ".join([f"{p1},{p2}" for p1, p2 in step.on_segments])
        
        # 3. Assemblage de la commande finale
        self.latex_parts.append(f"    \\tkzMarkSegments{options_str}({segments_str})")
    
    def _translate_calculate_length(self, step: "CalculateLength"):
        r"""Traduit le calcul de la longueur d'un segment."""
        # On réutilise la logique de nom de macro sécurisé + registre, éprouvée avec les angles.
        macro_name = ''.join(filter(str.isalpha, step.id))
        self.defined_calculations[step.id] = macro_name
        
        p1, p2 = step.between_points
        self.latex_parts.append(f"    \\tkzCalcLength({p1},{p2})")
        self.latex_parts.append(f"    \\tkzGetLength{{{macro_name}}}")


    def _translate_mark_right_angle(self, step: "MarkRightAngle"):
        # C'est un angle entre TROIS POINTS.
        # Ex: ABC, l'angle droit est en B. Donc vertex=B, points=(A,C).
        p1, p2 = step.points
        vertex = step.vertex
        self.latex_parts.append(f"    \\tkzMarkRightAngle({p1},{vertex},{p2})")

    def _translate_def_projection_point(self, step: "DefineProjectionPoint"):
        """
        Traduit la définition d'un point par projection orthogonale sur une ligne.
        Cette étape nécessite de retrouver les points qui définissent la ligne de destination.
        """
        # On cherche l'étape qui a défini la ligne 'on_line' pour retrouver ses points de base.
        line_def_step = self._find_line_def_step(step.on_line)
        if not line_def_step or not hasattr(line_def_step, 'through'):
            log.warning(f"Impossible de trouver la définition de la ligne ID '{step.on_line}' pour la projection. Étape ignorée.")
            return

        # La ligne de base est définie par deux points.
        p_ref1, p_ref2 = line_def_step.through
        
        # On construit la commande LaTeX
        self.latex_parts.append(
            f"    \\tkzDefPointBy[projection=onto {p_ref1}--{p_ref2}]({step.from_point}) \\tkzGetPoint{{{step.id}}}"
        )



    # ==============================================================================
#                      TRADUCTEURS POUR LES CERCLES
# ==============================================================================

    def _translate_def_circle_by_center_point(self, step: "DefineCircleByCenterPoint"):
        r"""
        Traduit la définition d'un cercle par centre et point.
        Étape 1 : Définit le cercle en LaTeX.
        Étape 2 : Enregistre les points nécessaires pour le dessin dans la mémoire interne.
        """
        # La définition LaTeX est simple, elle rend le cercle connu par tkz-euclide.
        # self.latex_parts.append(f"    \\tkzDefCircle({step.center},{step.through_point})")
        
        # Pour ce cas, les points de dessin sont triviaux : ce sont le centre
        # et le point de passage eux-mêmes. On les stocke dans notre dictionnaire.
        self.defined_circles[step.id] = (step.center, step.through_point)

    def _translate_def_circle_by_center_radius(self, step: "DefineCircleByCenterRadius"):
        r"""
        Traduit la définition d'un cercle par centre et rayon.
        Cette méthode applique le paradigme de calcul:
        1. Crée une macro LaTeX pour stocker la valeur numérique du rayon.
        2. Utilise tkzDefCircle[R] pour DÉFINIR le cercle (calcul).
        3. Capture un point sur ce nouveau cercle avec tkzGetPoint.
        4. Mémorise le centre et ce nouveau point pour le dessin futur.
        """
        # 1. Créer un nom unique et sûr pour la macro LaTeX qui stockera la longueur du rayon.
        # Ex: Pour un cercle id='c1', la macro sera \c1Radius
        radius_macro_name = f"\\{step.id}Radius"
        # 2. On définit la macro SANS unité. Ce sera une valeur pure (ex: "1.5").
        # tkz-euclide l'interprétera comme "1.5 * l'unité du graphique".
        self.latex_parts.append(f"    \\edef{radius_macro_name}{{{step.radius}}}")

        # 2. Créer un nom unique pour le point que nous allons capturer sur le cercle.
        # Ex: c1_on_circle
        point_on_circle_name = f"{step.id}_on_circle"

        # 3. Définir le cercle en LaTeX en utilisant l'option [R] et la macro,
        # puis CAPTURER immédiatement le pôle Est du cercle et le nommer.
        # Cette syntaxe chaînée avec \tkzGetPoint est validée par la documentation.
        self.latex_parts.append(
            f"    \\tkzDefCircle[R]({step.center},{radius_macro_name}) \\tkzGetPoint{{{point_on_circle_name}}}"
        )

        # 4. Mémoriser dans notre dictionnaire les informations pour l'étape de dessin.
        # Le centre est `step.center`. Le point sur le cercle est `point_on_circle_name`.
        self.defined_circles[step.id] = (step.center, point_on_circle_name)


    def _translate_def_circle_by_diameter(self, step: "DefineCircleByDiameter"):
        """
        Traduit la définition d'un cercle par son diamètre, en suivant la documentation.
        1. Utilise tkzDefCircle[diameter] pour DÉFINIR le cercle (calcul).
        2. Capture le CENTRE du cercle avec tkzGetPoint.
        3. Mémorise le centre et l'un des points du diamètre pour le dessin futur.
        """
        # 1. Extraire les deux points du diamètre.
        p1, p2 = step.diameter_points

        # 2. Créer un nom unique et prédictible pour le nouveau point (le centre)
        #    qui sera calculé par LaTeX.
        center_name = f"{step.id}_center"

        # 3. Générer la commande LaTeX pour définir le cercle ET capturer le centre.
        self.latex_parts.append(
            f"    \\tkzDefCircle[diameter]({p1},{p2}) \\tkzGetPoint{{{center_name}}}"
        )

        # 4. Mémoriser les informations nécessaires pour le dessin.
        # Le centre est celui que nous venons de calculer (`center_name`).
        # Le point sur le cercle est l'un des points du diamètre (ici, `p1`).
        self.defined_circles[step.id] = (center_name, p1)

    def _translate_def_circle_circumscribed(self, step: "DefineCircleCircumscribed"):
        """
        Traduit la définition du cercle circonscrit à 3 points.
        RECETTE DE LA DOC:
        1. Utilise tkzDefCircle[circum] ou tkzDefCircle(p1,p2,p3).
        2. Capture SEULEMENT le centre avec \tkzGetPoint.
        3. Mémorise ce centre et l'un des points de définition (qui est sur le cercle).
        """
        # 1. Extraire les trois points du triangle.
        p1, p2, p3 = step.through_points

        # 2. Créer un nom unique pour le centre à calculer.
        center_name = f"{step.id}_center"

        # 3. Définir le cercle ET capturer le centre. La commande \tkzDefCircle par défaut avec
        #    trois points est la circonscrite. Le chaînage avec \tkzGetPoint est validé par la doc.
        self.latex_parts.append(
            f"    \\tkzDefCircle({p1},{p2},{p3}) \\tkzGetPoint{{{center_name}}}"
        )

        # 4. Mémoriser les informations de dessin.
        # Le centre est `center_name`. Un point sur le cercle est, par définition, `p1`.
        self.defined_circles[step.id] = (center_name, p1)


    def _translate_def_circle_inscribed(self, step: "DefineCircleInscribed"):
        """
        Traduit la définition du cercle inscrit dans un triangle.
        RECETTE DE LA DOC:
        1. Utilise tkzDefCircle[in](p1,p2,p3).
        2. Capture le centre ET un point de tangence avec \tkzGetPoints (au pluriel).
        3. Mémorise ces deux nouveaux points pour le dessin.
        """
        # 1. Extraire les trois sommets du triangle.
        p1, p2, p3 = step.triangle_points

        # 2. Créer des noms uniques pour le centre ET le point de tangence.
        center_name = f"{step.id}_center"
        on_circle_name = f"{step.id}_on_circle" # Ce sera le point de tangence

        # 3. Définir le cercle avec l'option [in].
        self.latex_parts.append(f"    \\tkzDefCircle[in]({p1},{p2},{p3})")
        
        # 4. CAPTURER les deux points sur une nouvelle ligne (syntaxe plus sûre).
        self.latex_parts.append(f"    \\tkzGetPoints{{{center_name}}}{{{on_circle_name}}}")

        # 5. Mémoriser ces deux NOUVEAUX points pour le dessin.
        self.defined_circles[step.id] = (center_name, on_circle_name)


    def _translate_draw_circles(self, step: "DrawCircles"):
        """
        Dessine des cercles en lisant les informations de dessin préalablement
        stockées dans la mémoire interne (self.defined_circles).
        """
        # On utilise le nouvel helper pour le style.
        options_str = self._build_drawing_options(step.style)
        
        for circle_id in step.circle_ids:
            if circle_id in self.defined_circles:
                # On récupère le tuple (centre, point_sur_cercle) de notre mémoire.
                center, on_circle = self.defined_circles[circle_id]
                
                # On génère une commande de dessin simple et fiable pour chaque cercle.
                self.latex_parts.append(f"    \\tkzDrawCircle{options_str}({center},{on_circle})")
            else:
                log.warning(f"Impossible de dessiner le cercle ID '{circle_id}' car il n'a pas été défini ou sa définition a échoué.")
    
    def _translate_label_circle(self, step: "LabelCircle"):
        r"""Traduit l'action d'étiqueter un cercle."""
        # Pour les labels, les options de style sont généralement simples.
        options_str = f"[{step.style.color}]" if step.style and step.style.color else ""
        
        circle_def_str = f"({step.center_id},{step.point_on_circle_id})"
        angle_str = f"({step.angle})"
        label_str = f"{{{step.label}}}" if '$' in step.label else f"{{${step.label}$}}"

        self.latex_parts.append(
            f"    \\tkzLabelCircle{options_str}{circle_def_str}{angle_str}{label_str}"
        )

    def _translate_label_arc(self, step: "LabelArc"):
        r"""Traduit l'action d'étiqueter un arc."""
        options = [f"pos={step.pos}"]
        if step.style and step.style.color:
            options.append(step.style.color)
        options_str = f"[{','.join(options)}]"
        
        arc_def_str = f"({step.start_point_id},{step.center_id},{step.end_point_id})"
        label_str = f"{{{step.label}}}" if '$' in step.label else f"{{${step.label}$}}"
        
        self.latex_parts.append(f"    \\tkzLabelArc{options_str}{arc_def_str}{label_str}")

    # ==============================================================================
    #                 TRADUCTEURS POUR LES INTERSECTIONS
    # ==============================================================================

    def _translate_find_intersection_LL(self, step: "FindIntersectionLineLine"):
        r"""Traduit la recherche d'intersection entre deux droites."""
        l1_p1, l1_p2 = step.line1_points
        l2_p1, l2_p2 = step.line2_points
        # La syntaxe LaTeX est directe, avec \tkzGetPoint chaîné.
        # \tkzInterLL attend des parenthèses SIMPLES.
        line1_arg = f"({l1_p1},{l1_p2})"
        line2_arg = f"({l2_p1},{l2_p2})"
        
        # La définition et la capture sont sur des lignes séparées.
        self.latex_parts.append(
            f"    \\tkzInterLL{line1_arg}{line2_arg} \\tkzGetPoint{{{step.id}}}"
        )

    def _translate_find_intersection_LC(self, step: "FindIntersectionLineCircle"):
        r"""Traduit la recherche d'intersection entre une droite et un cercle."""
        # 1. Formater la partie 'droite' de la commande.
        line_p1, line_p2 = step.line_points
        line_arg = f"({line_p1},{line_p2})"
        
        # 2. Utiliser notre helper pour formater la partie 'cercle'.
        circle_arg = self._format_circle_inter_arg(step.circle_def, name_hint=step.ids[0])
        
        # 3. Construire la commande et la capture de points (sur une nouvelle ligne pour la clarté).
        # BON PATTERN POUR LC : on capture le résultat IMMÉDIATEMENT.
        self.latex_parts.append(
            f"    \\tkzInterLC{line_arg}{circle_arg} \\tkzGetPoints{{{step.ids[0]}}}{{{step.ids[1]}}}"
        )

    def _translate_find_intersection_CC(self, step: "FindIntersectionCircleCircle"):
        r"""Traduit la recherche d'intersection entre deux cercles."""
        # 1. Utiliser notre helper pour les deux arguments 'cercle'.
        # Pour \tkzInterCC, les arguments sont dans des DOUBLES parenthèses.
        circle1_arg = self._format_circle_inter_arg(step.circle1_def, name_hint=step.ids[0])
        circle2_arg = self._format_circle_inter_arg(step.circle2_def, name_hint=step.ids[1])
        
        # 2. Construire la commande et la capture de points.
        # La définition et la capture sont sur des lignes séparées.
        # BON PATTERN POUR CC : on capture le résultat IMMÉDIATEMENT.
        self.latex_parts.append(
            f"    \\tkzInterCC{circle1_arg}{circle2_arg} \\tkzGetPoints{{{step.ids[0]}}}{{{step.ids[1]}}}"
        )


    def _translate_def_tangent_at_point(self, step: "DefineTangentAtPointOnCircle"):
        r"""CALCULE une tangente en un point du cercle et mémorise la ligne."""
        # Syntaxe de la doc : on calcule la ligne...
        command = f"    \\tkzDefLine[tangent at={step.at_point_id}]({step.circle_center_id})"
        
        # ...et sur la même ligne, on capture un second point sur la tangente.
        # Nous donnons à ce nouveau point le même nom que l'ID de la ligne pour la simplicité.
        self.latex_parts.append(f"{command} \\tkzGetPoint{{{step.id}}}")
        
        # On mémorise la paire de points de dessin : le point de tangence et ce nouveau point.
        self.defined_lines[step.id] = (step.at_point_id, step.id)


    def _translate_def_tangents_from_point(self, step: "DefineTangentsFromPointToCircle"):
        r"""CALCULE les points de tangence d'un point extérieur, puis déclare les deux lignes."""
        # D'abord, on formate l'argument du cercle avec notre helper.
        circle_arg_content = self._format_circle_inter_arg(step.circle_def, name_hint=step.from_point_id)
        
        # 1. On calcule et capture les DEUX points de tangence.
        self.latex_parts.append(f"    \\tkzDefLine[tangent from={step.from_point_id}]{circle_arg_content}")
        self.latex_parts.append(f"    \\tkzGetPoints{{{step.tangency_point_ids[0]}}}{{{step.tangency_point_ids[1]}}}")

        # 2. Maintenant que les points de tangence sont créés, on DÉCLARE (en Python)
        #    les deux lignes dans notre mémoire pour pouvoir les dessiner.
        # La première tangente relie le point extérieur au premier point de tangence.
        self.defined_lines[step.line_ids[0]] = (step.from_point_id, step.tangency_point_ids[0])
        # La seconde tangente relie le point extérieur au second point de tangence.
        self.defined_lines[step.line_ids[1]] = (step.from_point_id, step.tangency_point_ids[1])
    

    def _translate_draw_ellipse(self, step: "DrawEllipse"):
        """Traduit l'action de dessiner une ellipse."""
        options_str = self._build_drawing_options(step.style)
        # On se fie à la syntaxe de l'EXEMPLE, avec des simples parenthèses.
        args_str = f"({step.center_id},{step.semi_major_axis},{step.semi_minor_axis},{step.angle})"
        self.latex_parts.append(f"    \\tkzDrawEllipse{options_str}{args_str}")

    def _translate_draw_semi_circles(self, step: "DrawSemiCircles"):
        """Traduit l'action de dessiner un ou plusieurs demi-cercles."""
        options_str = self._build_drawing_options(step.style)
        
        # On transforme [('O','A'), ('C','D')] en la chaîne "O,A C,D"
        segments_str = " ".join([f"{center},{point}" for center, point in step.segments])
        
        # On assemble la commande finale, qui est robuste pour un ou plusieurs segments.
        self.latex_parts.append(f"    \\tkzDrawSemiCircles{options_str}({segments_str})")


    def _translate_draw_arc_by_points(self, step: "DrawArcByPoints"):
        """Traduit l'action de dessiner un arc défini par son centre et deux points."""
        # On utilise une copie du style pour y ajouter l'option de flèche si elle existe.
        style = step.style.model_copy()
        options = []
        if style.color: options.append(style.color)
        if style.thickness: options.append(style.thickness)
        if style.pattern: options.append(style.pattern)
        if step.arrow_spec: options.append(step.arrow_spec) # Ajout de la flèche
        options_str = f"[{','.join(options)}]" if options else ""

        # La syntaxe est (Centre,Depart)(Arrivee)
        arg1 = f"({step.center_id},{step.start_point_id})"
        arg2 = f"({step.end_point_id})"
        
        self.latex_parts.append(f"    \\tkzDrawArc{options_str}{arg1}{arg2}")

    def _translate_draw_arc_by_angles(self, step: "DrawArcByAngles"):
        """Traduit l'action de dessiner un arc défini par son centre, rayon et angles."""
        style = step.style.model_copy()
        options = ['R'] # L'option 'R' est obligatoire pour ce mode
        # On construit les options de style avec le formatage clé=valeur
        if style.color: options.append(f"color={style.color}")
        if style.thickness: options.append(style.thickness)
        if style.pattern: options.append(style.pattern)
        if step.arrow_spec: options.append(step.arrow_spec)
        options_str = f"[{','.join(options)}]" if options else ""
        
        # La syntaxe est (Centre,Rayon)(AngleDepart,AngleArrivee)
        arg1 = f"({step.center_id},{step.radius})"
        arg2 = f"({step.start_angle},{step.end_angle})"
        
        self.latex_parts.append(f"    \\tkzDrawArc{options_str}{arg1}{arg2}")


    def _translate_def_point_on_line(self, step: "DefinePointOnLine"):
        r"""Traduit le calcul d'un point sur une ligne (syntaxe chaînée)."""
        p1, p2 = step.on_line_from_points
        options_str = f"[pos={step.pos}]"
        line_arg = f"({p1},{p2})"
        self.latex_parts.append(
            f"    \\tkzDefPointOnLine{options_str}{line_arg} \\tkzGetPoint{{{step.id}}}"
        )

    def _translate_def_point_on_circle(self, step: "DefinePointOnCircle"):
        r"""Traduit le calcul d'un point sur un cercle (syntaxe chaînée)."""
        options = []
        # Le contenu de l'option change selon le mode choisi.
        if step.radius_from_point_id:
            options.append(f"through = center {step.center_id} angle {step.angle} point {step.radius_from_point_id}")
        elif step.radius_as_value is not None:
            options.append(f"R = center {step.center_id} angle {step.angle} radius {step.radius_as_value}")

        options_str = f"[{','.join(options)}]"
        self.latex_parts.append(
            f"    \\tkzDefPointOnCircle{options_str} \\tkzGetPoint{{{step.id}}}"
        )
    
    def _translate_draw_angle(self, step: "DrawAngle"):
        r"""Traduit l'action de dessiner un angle en la transformant en une action DrawSegments."""
        
        # 1. On extrait les points de la définition de l'angle.
        side_pt1, vertex, side_pt2 = step.of_angle_from_points
        
        # 2. On prépare la liste des deux segments à dessiner.
        segments_to_draw = [
            [side_pt1, vertex],  # Premier côté de l'angle
            [vertex, side_pt2]   # Deuxième côté de l'angle
        ]
        
        # 3. On crée un objet "step" DrawSegments temporaire à la volée.
        #    C'est ici qu'est la "magie" : on délègue le travail à notre outil existant et robuste.
        temp_draw_segments_step = DrawSegments(
            segments=segments_to_draw,
            style=step.style
        )
        
        # 4. On appelle le traducteur existant. Aucune nouvelle logique LaTeX n'est nécessaire.
        self._translate_draw_segments(temp_draw_segments_step)


    def _translate_calculate_angle_by_points(self, step: "CalculateAngleByPoints"):
        r"""Traduit le calcul d'un angle à partir de trois points."""

        # On nettoie l'ID pour créer un nom de macro LaTeX valide (lettres uniquement).
        macro_name = ''.join(filter(str.isalpha, step.id))

        # ON MÉMORISE LE LIEN : "ID d'origine" -> "nom de macro propre"
        self.defined_calculations[step.id] = macro_name
        
        # On calcule...
        self.latex_parts.append(
            f"    \\tkzFindAngle({step.start_point_id},{step.vertex_id},{step.end_point_id})"
        )
        # ...puis on récupère le résultat dans une macro. Le nom de la macro doit commencer
        # par une lettre, # CORRECTION : On ne préfixe plus l'ID. On le transforme directement en macro.
        # Ex: "angle_b" devient {\angle_b}
        self.latex_parts.append(f"    \\tkzGetAngle{{{macro_name}}}")

    def _translate_calculate_angle_of_slope(self, step: "CalculateAngleOfSlope"):
        r"""Traduit le calcul de l'angle de pente d'une ligne."""
        macro_name = ''.join(filter(str.isalpha, step.id))
        # ON MÉMORISE LE LIEN : "ID d'origine" -> "nom de macro propre"
        self.defined_calculations[step.id] = macro_name
        p1, p2 = step.line_points
        self.latex_parts.append(f"    \\tkzFindSlopeAngle({p1},{p2})")
       # Ex: "pente_bc" devient {\pente_bc}
        self.latex_parts.append(f"    \\tkzGetAngle{{{macro_name}}}")
    
    def _translate_def_angle_bisector(self, step: "DefineAngleBisector"):
        r"""Traduit la définition d'une ligne bissectrice."""
        # 1. On extrait les points et on nomme clairement le sommet.
        start_pt, vertex_pt, end_pt = step.of_angle_from_points

        # 2. On crée un nom unique pour le point que LaTeX va calculer sur la bissectrice.
        #    Cette convention le rend identifiable et évite les conflits.
        calculated_point_name = step.point_on_line_id
        
        # 3. On construit la commande LaTeX
        options_str = "[bisector]"
        points_str = f"({start_pt},{vertex_pt},{end_pt})"
        self.latex_parts.append(f"    \\tkzDefLine{options_str}{points_str} \\tkzGetPoint{{{calculated_point_name}}}")
        
        # 4. CRUCIAL : On met à jour notre registre des lignes définies.
        #    La bissectrice est maintenant une ligne définie par le sommet et le point calculé.
        self.defined_lines[step.line_id] = (vertex_pt, calculated_point_name)

        # --- L'AJOUT CRUCIAL ---
        # On écrit la recette de naissance dans notre mémoire.
        # C'est cette information qui sera lue par _translate_mark_internal_angle.
        self.point_construction_methods[calculated_point_name] = {
            'type': 'bisector_definition',
            'of_angle': (start_pt, vertex_pt, end_pt)
        }


    def _translate_draw_text(self, step: "DrawText"):
        r"""Traduit l'action d'écrire du texte à une position."""
        x, y = step.coords
        options_str = f"[color={step.style.color}]" if step.style and step.style.color else ""
        text_to_render = ""

        # CAS 1 : Affichage d'un texte simple 
        if step.text is not None:
            text_to_render = step.text
            if not (text_to_render.startswith('\\') or '$' in text_to_render):
                 text_to_render = f"\\text{{{text_to_render}}}"
        
        # CAS 2 : Affichage intelligent d'un calcul
        elif step.display_calculation is not None:
            params = step.display_calculation
            calc_id = params.id_of_calculation
            
            # On utilise notre "registre" pour trouver le nom de macro LaTeX filtré et sûr.
            if calc_id in self.defined_calculations:
                macro_name = self.defined_calculations[calc_id]
                # On construit la commande LaTeX pour afficher la valeur.
                value_str = f"$\\pgfmathprintnumber{{\\{macro_name}}}$"
                # On injecte cette commande dans le modèle de l'utilisateur.
                text_to_render = params.format_template.format(value_str)
            else:
                log.warning(f"ID de calcul '{calc_id}' non trouvé pour DrawText.")
                text_to_render = f"\\text{{ERREUR: Calcul '{calc_id}' introuvable}}"
        
        # Commande de dessin finale
        self.latex_parts.append(f"    \\draw{options_str} ({x},{y}) node {{{text_to_render}}};")

    def _translate_mark_angle(self, step: "MarkAngle"):
        # NOTE TRES IMPORTANTE: ne jamains exposé cette solution au llm, ils doivent toujours utiliser 
        # NOTE: "_translate_mark_internal_angle"
        r"""
        Traduit l'action de marquer un angle en générant les commandes LaTeX
        appropriées pour le remplissage, le trait de l'arc, et l'étiquette.
        """
        style = step.style
        points_str = f"({step.start_point_id},{step.vertex_id},{step.end_point_id})"

        final_label_text = None
        # 1. reflexion sur Étiquette 
        if step.display_calculated_angle_id:
            # On recherche le nom propre de la macro dans notre mémoire
            calc_id = step.display_calculated_angle_id
            if calc_id in self.defined_calculations:
                macro_name_to_use = self.defined_calculations[calc_id]
                # On construit nous-mêmes la chaîne LaTeX, garantissant qu'elle est correcte
                final_label_text = f"$\\pgfmathprintnumber{{\\{macro_name_to_use}}}^\\circ$"
            else:
                log.warning(f"Calcul d'angle avec l'ID '{calc_id}' non trouvé.")
        elif step.label:
            final_label_text = step.label if '$' in step.label else f"${step.label}$"

        # 2. Remplissage (si demandé)
        if style.fill_color:
            fill_options = f"[fill={style.fill_color},size={step.size},opacity={style.opacity or 0.2}]"
            self.latex_parts.append(f"    \\tkzFillAngle{fill_options}{points_str}")

        # 3. Dessin de l'arc
        mark_options_list = [f"size={step.size}"]
        if style.color: mark_options_list.append(style.color)
        if style.thickness: mark_options_list.append(style.thickness)
        if style.pattern: mark_options_list.append(style.pattern)
        mark_options_str = f"[{','.join(mark_options_list)}]"
        self.latex_parts.append(f"    \\tkzMarkAngle{mark_options_str}{points_str}")

        # 4. Étiquette de l'angle (si demandée)
        if final_label_text:
            label_options = f"[pos={step.label_pos}]"
            self.latex_parts.append(f"    \\tkzLabelAngle{label_options}{points_str}{{{final_label_text}}}")


    def _translate_mark_internal_angle(self, step: "MarkInternalAngle"):
        r"""
        Traduit l'action de marquer un angle interne.
        Calcule l'orientation et appelle le traducteur `_mark_angle` avec les bons paramètres.
        """
        p1_id, vertex_id, p2_id = step.points

        # --- La nouvelle logique de décision ---
        # On initialise avec un ordre par défaut; l'ordre donné par l'utilisateur/llm
        start_point = p1_id
        end_point = p2_id
        
        # On identifie quel point (p1 ou p2) est celui qui a été calculé.
        # Dans notre cas 'points': ('C', 'A', 'B'), p1_id='C'
        # Notre sommet est 'A'. Le point "problème" est 'C'.
        calculated_point_id = None
        if p1_id not in self.point_construction_methods or self.point_construction_methods[p1_id]['type'] != 'coords':
            calculated_point_id = p1_id
            other_point_id = p2_id
        elif p2_id not in self.point_construction_methods or self.point_construction_methods[p2_id]['type'] != 'coords':
            calculated_point_id = p2_id
            other_point_id = p1_id

        # Si on a bien un point calculé, on applique les règles de prédiction.
        if calculated_point_id:
            recipe = self.point_construction_methods.get(calculated_point_id)
            
            # --- Règle 1 : Cas des Triangles ---
            # Règle pour les points issus de la définition d'un triangle
            if recipe and recipe['type'] == 'triangle_definition':
                base_p1, base_p2 = recipe['base']

                # Cas 1 : Le sommet de notre angle est le PREMIER point de la base du triangle.
                if vertex_id == base_p1:
                    # Si non-inversé, l'ordre est base_p2 -> point_calculé
                    if not recipe['swap']:
                        start_point, end_point = base_p2, calculated_point_id
                    # Si inversé, l'ordre est point_calculé -> base_p2
                    else:
                        start_point, end_point = calculated_point_id, base_p2

                # Cas 2 : Le sommet de notre angle est le SECOND point de la base du triangle.
                elif vertex_id == base_p2:
                    # Si non-inversé, l'ordre est point_calculé -> base_p1
                    if not recipe['swap']:
                        start_point, end_point = calculated_point_id, base_p1
                    # Si inversé, l'ordre est base_p1 -> point_calculé
                    else:
                        start_point, end_point = base_p1, calculated_point_id

            # --- Règle 2 : CAS DE LA BISSECTRICE (L'AJOUT) ---
            elif recipe and recipe['type'] == 'bisector_definition':
                # La bissectrice est, par définition, à l'intérieur de l'angle.
                # L'ordre logique anti-horaire sera donc toujours :
                #   point_départ -> bissectrice -> point_arrivée
                angle_start_pt, angle_vertex, angle_end_pt = recipe['of_angle']
                
                # Si le sommet est bien celui de l'angle d'origine...
                if vertex_id == angle_vertex:
                    # L'ordre B -> P_bis est forcément correct.
                    # L'ordre P_bis -> C est forcément correct.
                    # Donc l'ordre B -> C est le chemin externe.
                    
                    # La question est : Est-ce qu'on marque B-A-P_bis ou C-A-P_bis ?
                    # p1_id est soit 'B' ou 'C'.
                    # Si le point 'other_point_id' est bien le début de l'angle
                    # d'origine (B), on peut en déduire le bon ordre.
                    if p1_id == calculated_point_id : other_point_id = p2_id
                    else: other_point_id = p1_id

                    if other_point_id == angle_start_pt:
                        start_point, end_point = other_point_id, calculated_point_id
                    elif other_point_id == angle_end_pt:
                        start_point, end_point = calculated_point_id, other_point_id
        
        # S'il n'y avait aucun point calculé (que des points manuels),
        # on garde la vieille méthode de calcul par coordonnées.
        # C'est la garantie de non-régression.
        else:
            p1_coords = self._get_coords_by_id(p1_id)
            vertex_coords = self._get_coords_by_id(vertex_id)
            p2_coords = self._get_coords_by_id(p2_id)
            
            if all([p1_coords, vertex_coords, p2_coords]):
                v1 = (p1_coords[0] - vertex_coords[0], p1_coords[1] - vertex_coords[1])
                v2 = (p2_coords[0] - vertex_coords[0], p2_coords[1] - vertex_coords[1])
                cross_product = v1[0] * v2[1] - v1[1] * v2[0]
                if cross_product <= 0:
                    start_point, end_point = p2_id, p1_id

        # --- Fin de la logique ---

        # On délègue à l'outil simple MarkAngle avec l'ordre GARANTI correct.
        temp_mark_step = MarkAngle(
            vertex_id=vertex_id,
            start_point_id=start_point,
            end_point_id=end_point,
            label=step.label,
            display_calculated_angle_id=step.display_calculated_angle_id,
            size=step.size,
            label_pos=step.label_pos,
            style=step.style
        )
        self._translate_mark_angle(temp_mark_step)


    def _translate_draw_sector_by_points(self, step: "DrawAngularSectorByPoints"):
        r"""Traduit le dessin d'un secteur défini par trois points.
        Il calcule le sens de balayage pour TOUJOURS dessiner le plus petit secteur.
        """
        # L'option 'towards' est le défaut, pas besoin de la spécifier.
        center = self._get_coords_by_id(step.center_id)
        start = self._get_coords_by_id(step.start_point_id)
        end = self._get_coords_by_id(step.end_point_id)
        
        start_id = step.start_point_id
        end_id = step.end_point_id

        if all([center, start, end]):
            # Calcul vectoriel pour déterminer le chemin le plus court.
            vec_start = (start[0] - center[0], start[1] - center[1])
            vec_end = (end[0] - center[0], end[1] - center[1])
            cross_product = vec_start[0] * vec_end[1] - vec_start[1] * vec_end[0]
            
            # La règle de tkz est : anti-horaire.
            # Si le produit vectoriel est négatif, le chemin court est dans le
            # sens horaire, donc on doit INVERSER les points pour forcer tkz
            # à prendre le petit chemin dans le sens anti-horaire.
            if cross_product < 0:
                start_id, end_id = end_id, start_id

        options_str = self._build_drawing_options(step.style)
        arg1 = f"({step.center_id},{start_id})" # Utilise les ID potentiellement inversés
        arg2 = f"({end_id})"
        self.latex_parts.append(f"    \\tkzDrawSector{options_str}{arg1}{arg2}")


    def _translate_draw_sector_by_rotation(self, step: "DrawAngularSectorByRotation"):
        r"""Traduit le dessin d'un secteur défini par rotation."""
        # On ajoute l'option 'rotate' aux autres options de style.
        style = step.style
        options = ['rotate']
        if style.color: options.append(f"color={style.color}")
        if style.thickness: options.append(style.thickness)
        if style.pattern: options.append(style.pattern)
        if style.fill_color: options.append(f"fill={style.fill_color}")
        if style.opacity is not None: options.append(f"opacity={style.opacity}")
        options_str = f"[{','.join(options)}]"

        arg1 = f"({step.center_id},{step.start_point_id})"
        arg2 = f"({step.angle})"
        self.latex_parts.append(f"    \\tkzDrawSector{options_str}{arg1}{arg2}")

    def _translate_draw_sector_by_angles(self, step: "DrawAngularSectorByAngles"):
        r"""Traduit le dessin d'un secteur défini par rayon et angles."""
        style = step.style
        options = ['R'] # L'option 'R' est la base
        if style.color: options.append(f"color={style.color}") # En mode [R], la couleur est clé=valeur
        if style.thickness: options.append(style.thickness)
        if style.pattern: options.append(style.pattern)
        if style.fill_color: options.append(f"fill={style.fill_color}")
        if style.opacity is not None: options.append(f"opacity={style.opacity}")
        options_str = f"[{','.join(options)}]"

        arg1 = f"({step.center_id},{step.radius})"
        arg2 = f"({step.start_angle},{step.end_angle})"
        self.latex_parts.append(f"    \\tkzDrawSector{options_str}{arg1}{arg2}")

    def _translate_draw_sector_by_nodes(self, step: "DrawAngularSectorByNodes"):
        r"""Traduit le dessin d'un secteur défini par rayon et points cibles.
         Il calcule le sens de balayage pour TOUJOURS dessiner le plus petit secteur."""
        center = self._get_coords_by_id(step.center_id)
        node1 = self._get_coords_by_id(step.node1_id)
        node2 = self._get_coords_by_id(step.node2_id)
        
        # On initialise nos variables locales avec les valeurs du step
        node1_id_to_use = step.node1_id
        node2_id_to_use = step.node2_id

        if all([center, node1, node2]):
            vec1 = (node1[0] - center[0], node1[1] - center[1])
            vec2 = (node2[0] - center[0], node2[1] - center[1])
            cross_product = vec1[0] * vec2[1] - vec1[1] * vec2[0]

            if  cross_product < 0:
                node1_id_to_use, node2_id_to_use = step.node2_id, step.node1_id

        style = step.style
        options = ['R with nodes'] # L'option de base
        if style.color: options.append(f"color={style.color}")
        if style.thickness: options.append(style.thickness)
        if style.pattern: options.append(style.pattern)
        if style.fill_color: options.append(f"fill={style.fill_color}")
        if style.opacity is not None: options.append(f"opacity={style.opacity}")
        options_str = f"[{','.join(options)}]"

        arg1 = f"({step.center_id},{step.radius})"
        arg2 = f"({node1_id_to_use},{node2_id_to_use})"
        self.latex_parts.append(f"    \\tkzDrawSector{options_str}{arg1}{arg2}")

    
    def _translate_def_triangle_by_2_points(self, step: "DefineTriangleBy2Points"):
        r"""Traduit la définition d'un triangle via \tkzDefTriangle."""
        options = []
        
        # 1. Gérer le type de triangle et ses options spécifiques
        if step.triangle_type == 'two_angles':
            # La doc utilise 'two angles=50 and 70', nous le formatons ici.
            angle1, angle2 = step.angles
            options.append(f"two angles={angle1} and {angle2}")
        elif step.triangle_type == 'isoceles_right':
            # Le modèle a 'isoceles_right', mais LaTeX attend 'isoceles right'.
            options.append("isoceles right")
        else:
            # Pour equilateral, school, pythagore, le nom est le même.
            options.append(step.triangle_type)

        # 2. Gérer l'option de symétrie
        if step.swap:# ne fonctionne pas avec l'option school
            options.append("swap")

        # 3. Assembler la commande
        options_str = f"[{','.join(options)}]"
        points_str = f"({step.on_segment[0]},{step.on_segment[1]})"
        
        # 4. Générer la commande finale avec capture du nouveau point
        self.latex_parts.append(
            f"    \\tkzDefTriangle{options_str}{points_str} \\tkzGetPoint{{{step.id}}}"
        )
        # Et on enregistre sa recette ! C'est la clé.
        self.point_construction_methods[step.id] = {
            'type': 'triangle_definition',
            'base': step.on_segment,
            'triangle_type': step.triangle_type,
            'swap': step.swap
        }

    def _translate_def_triangle_center(self, step: "DefineTriangleCenter"):
        r"""Traduit la définition d'un point remarquable d'un triangle."""
        # Dictionnaire pour mapper nos noms clairs aux options courtes de LaTeX
        type_map = {
            "orthocenter": "ortho",
            "centroid": "centroid",
            "circumcenter": "circum",
            "incenter": "in",
            "bisector_center": "in" # L'alias pointe vers la même option LaTeX
        }
        latex_option = type_map[step.center_type]

        options_str = f"[{latex_option}]"
        points_str = f"({','.join(step.from_triangle_points)})"

        # Générer la commande finale avec capture du nouveau point
        self.latex_parts.append(
            f"    \\tkzDefTriangleCenter{options_str}{points_str} \\tkzGetPoint{{{step.id}}}"
        )
    
    def _translate_def_square(self, step: "DefineSquare"):
        r"""Traduit la définition des points d'un carré."""
        points_str = f"({','.join(step.from_points)})"
        new_ids_str = f"{{{step.ids[0]}}}{{{step.ids[1]}}}"
        
        # On calcule PUIS on capture les nouveaux points
        self.latex_parts.append(f"    \\tkzDefSquare{points_str}")
        self.latex_parts.append(f"    \\tkzGetPoints{new_ids_str}")

    def _translate_def_rectangle(self, step: "DefineRectangle"):
        r"""Traduit la définition des points d'un rectangle."""
        points_str = f"({','.join(step.from_diagonal)})"
        new_ids_str = f"{{{step.ids[0]}}}{{{step.ids[1]}}}"

        # On calcule PUIS on capture les nouveaux points
        self.latex_parts.append(f"    \\tkzDefRectangle{points_str}")
        self.latex_parts.append(f"    \\tkzGetPoints{new_ids_str}")
    
    def _translate_def_parallelogram(self, step: "DefineParallelogram"):
        r"""Traduit la définition du point d'un parallélogramme."""
        points_str = f"({','.join(step.from_points)})"
        
        # On calcule ET on capture le nouveau point sur la même ligne
        self.latex_parts.append(
            f"    \\tkzDefParallelogram{points_str} \\tkzGetPoint{{{step.id}}}"
        )


     
    def _translate_def_points_by_translation(self, step: "DefinePointsByTranslation"):
        # Syntaxe correcte: from P1 to P2
        options_str = f"[translation=from {step.by.from_point} to {step.by.to_point}]"
        points_str = f"({','.join(step.points_to_transform)})"
        new_ids_str = f"{{{','.join(step.new_ids)}}}"
        self.latex_parts.append(f"    \\tkzDefPointsBy{options_str}{points_str}{new_ids_str}")

    def _translate_def_points_by_homothety(self, step: "DefinePointsByHomothety"):
        # Syntaxe correcte: center P ratio R
        options_str = f"[homothety=center {step.by.center} ratio {step.by.ratio}]"
        points_str = f"({','.join(step.points_to_transform)})"
        new_ids_str = f"{{{','.join(step.new_ids)}}}"
        self.latex_parts.append(f"    \\tkzDefPointsBy{options_str}{points_str}{new_ids_str}")
        
    def _translate_def_points_by_reflection(self, step: "DefinePointsByReflection"):
        # Syntaxe correcte et cruciale: over P1--P2 (avec double tiret)
        p1, p2 = step.by.over_line_from_points
        options_str = f"[reflection=over {p1}--{p2}]"
        points_str = f"({','.join(step.points_to_transform)})"
        new_ids_str = f"{{{','.join(step.new_ids)}}}"
        self.latex_parts.append(f"    \\tkzDefPointsBy{options_str}{points_str}{new_ids_str}")

    def _translate_def_points_by_symmetry(self, step: "DefinePointsBySymmetry"):
        # Syntaxe correcte: center P
        options_str = f"[symmetry=center {step.by.center}]"
        points_str = f"({','.join(step.points_to_transform)})"
        new_ids_str = f"{{{','.join(step.new_ids)}}}"
        self.latex_parts.append(f"    \\tkzDefPointsBy{options_str}{points_str}{new_ids_str}")
        
    def _translate_def_points_by_rotation(self, step: "DefinePointsByRotation"):
        # Syntaxe correcte: center P angle A
        options_str = f"[rotation=center {step.by.center} angle {step.by.angle}]"
        points_str = f"({','.join(step.points_to_transform)})"
        new_ids_str = f"{{{','.join(step.new_ids)}}}"
        self.latex_parts.append(f"    \\tkzDefPointsBy{options_str}{points_str}{new_ids_str}")

    
    def _translate_fill_shape_with_pattern(self, step: "FillShapeWithPattern"):
        """Traduit l'action de remplissage par hachurage."""
        style = step.style
        options = [f"pattern={style.pattern_name}", f"pattern color={style.color}"]
        if style.pattern_thickness:
            options.append(style.pattern_thickness)
        
        options_str = f"[{','.join(options)}]"
        points_str = ",".join(step.point_ids)
        
        self.latex_parts.append(f"    \\tkzFillPolygon{options_str}({points_str})")


    def _translate_def_perspective_cuboid(self, step: "DefinePerspectiveCuboid"):
        """
        Traduit la construction déterministe d'un pavé en perspective.
        Définit les 4 points de la base avant, puis translate pour les 4 de l'arrière.
        """
        # 1. On récupère les noms de points définis par l'utilisateur.
        p_a, p_b, p_f, p_e = step.base_points
        p_d, p_c, p_g, p_h = step.derived_points
        
        # 2. On récupère les dimensions
        o_x, o_y = step.base_origin
        w = step.base_width
        h = step.base_height
        dv_x, dv_y = step.depth_vector
        
        # 3. Définition des 4 points de la face avant
        self.latex_parts.append(f"    \\tkzDefPoint({o_x}, {o_y}){{{p_a}}}")             # Ex: A
        self.latex_parts.append(f"    \\tkzDefPoint({o_x + w}, {o_y}){{{p_b}}}")         # Ex: B
        self.latex_parts.append(f"    \\tkzDefPoint({o_x + w}, {o_y + h}){{{p_f}}}")         # Ex: F
        self.latex_parts.append(f"    \\tkzDefPoint({o_x}, {o_y + h}){{{p_e}}}")             # Ex: E
        
        # 4. Création des 4 points arrière par translation
        #    On doit créer un vecteur de translation pour LaTeX. C'est plus propre.
        vec_start_name = f"{p_a}_trans_start"
        vec_end_name = f"{p_a}_trans_end"
        self.latex_parts.append(f"    \\tkzDefPoint({o_x}, {o_y}){{{vec_start_name}}}")
        self.latex_parts.append(f"    \\tkzDefPoint({o_x + dv_x}, {o_y + dv_y}){{{vec_end_name}}}")

        self.latex_parts.append(f"    \\tkzDefPointBy[translation=from {vec_start_name} to {vec_end_name}]({p_a}) \\tkzGetPoint{{{p_d}}}")
        self.latex_parts.append(f"    \\tkzDefPointBy[translation=from {vec_start_name} to {vec_end_name}]({p_b}) \\tkzGetPoint{{{p_c}}}")
        self.latex_parts.append(f"    \\tkzDefPointBy[translation=from {vec_start_name} to {vec_end_name}]({p_f}) \\tkzGetPoint{{{p_g}}}")
        self.latex_parts.append(f"    \\tkzDefPointBy[translation=from {vec_start_name} to {vec_end_name}]({p_e}) \\tkzGetPoint{{{p_h}}}")


# todo: lors de l'ecriture du guide; penser a mettre un champ sur l'intention du user afin de guider le llm

"""
# todo : Plan d'action pour le futur (Sprint "Style et Finitions") :
Nous pourrions ajouter à notre objet Style dans geometry2D_models.py un champ :
"line_extension": [0.2, 0.2] # [début, fin]
Notre traducteur ajouterait alors add = 0.2 and 0.2 aux options, ce qui permettrait de contrôler 
précisément la longueur "visuelle" des droites. Pour l'instant, gardons cela en tête comme une amélioration future.
"""
# ==============================================================================
#                      LA FONCTION PUBLIQUE DE L'OUTIL
# ==============================================================================

def generate_geometry_2d(
    input_data: Geometry2DInput, 
    show_axes: bool = False, 
    show_grid: bool = False
) -> Path:
    """Fonction principale de l'outil de géométrie 2D (Sprint 1 - Points et Lignes).
    Args:
        input_data (Geometry2DInput): Les données d'entrée validées par Pydantic.
        show_axes (bool): Si True, dessine les axes du repère.
        show_grid (bool): Si True, dessine la grille du repère.
    
    """
    log.info("Début de la génération de la figure de géométrie 2D.")
    
    try:
        translator = TkzEuclideTranslator(input_data, show_axes=show_axes, show_grid=show_grid)
        latex_code = translator.translate()
        log.info("Traduction en code LaTeX (tkz-euclide) réussie.")
        log.debug(f"Code LaTeX généré : \n{latex_code}")
        
        image_path = compile_latex_to_image(latex_code)
        log.info(f"Compilation LaTeX réussie. Image : {image_path}")
        return image_path
        
    except Exception as e:
        log.error(f"Échec dans le workflow de l'outil de géométrie : {e}", exc_info=True)
        raise e