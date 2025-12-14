# backend/src/features/geometry/models.py

from pydantic import BaseModel, Field, model_validator, field_validator, conint
from typing import List, Dict, Literal, Optional, Tuple, Union, Annotated

# ==============================================================================
#  MODÈLES DE SUPPORT (Version minimale pour le Sprint 1)
# ==============================================================================

class FigureConfig(BaseModel):
    """Configuration du cadre de la figure géométrique."""
    x_range: Tuple[float, float] = [-5, 5]
    y_range: Tuple[float, float] = [-5, 5]
    axes: bool = False
    grid: bool = False
    unit: str = "cm"

# --- Pour plus tard, mais on peut déjà définir une base ---
class Style(BaseModel):
    """Définit le style visuel d'un élément."""
    color: str = "black"
    thickness: Optional[Literal["thin", "thick", "very thick"]] = None
    pattern: Optional[Literal["dashed", "dotted"]] = None
    # --- AJOUTS POUR LES SURFACES ---
    fill_color: Optional[str] = Field(None, description="Couleur de remplissage pour les surfaces (cercles, polygones).")
    opacity: Optional[float] = Field(None, description="Opacité du remplissage (de 0.0 à 1.0).")
    
# ==============================================================================
#  MODÈLES D'ÉTAPES DE CONSTRUCTION (Version minimale pour le Sprint 1)
# ==============================================================================

# ==============================================================================
#  ÉTAPES DE CONSTRUCTION : Une Grammaire Complète pour les Points et Lignes
# ==============================================================================
# --- ACTIONS DE DÉFINITION DE POINTS ---
class DefinePointByCoords(BaseModel):
    type: Literal["def_point_coords"] = "def_point_coords"
    id: str
    coords: Tuple[float, float]
    label: Optional[str] = None
    style: Style = Field(default_factory=Style)

class DefineMidPoint(BaseModel):
    type: Literal["def_midpoint"] = "def_midpoint"
    id: str
    of_segment: Tuple[str, str] # (id_point_A, id_point_B)
    label: Optional[str] = None
    style: Style = Field(default_factory=Style)

# --- ACTIONS DE DÉFINITION DE LIGNES ---
class DefineLineByPoints(BaseModel):
    type: Literal["def_line_by_points"] = "def_line_by_points"
    id: str # L'ID de cette nouvelle ligne (ex: "d1")
    through: Tuple[str, str] # (id_point_A, id_point_B)


class DefineMediator(BaseModel):
    type: Literal["def_mediator"] = "def_mediator"
    id: str
    of_segment: Tuple[str, str]

class DefineProjectionPoint(BaseModel):
    type: Literal["def_projection_point"] = "def_projection_point"
    id: str
    from_point: str
    on_line: str # l'ID de la ligne

class DefineParallelLine(BaseModel):
    """
    Définit une nouvelle ligne qui est parallèle à une autre.
    Cette action est une définition pure ; pour la rendre visible, utilisez DrawLines.
    Elle se traduit directement en LaTeX par :
    \\tkzDefLine[parallel=through {through_point}]({p_ref1},{p_ref2})
    """
    type: Literal["def_parallel_line"] = "def_parallel_line"
    id: str                          # L'ID de notre nouvelle ligne (ex: "d1_par_C")
    through_point: str               # L'ID du point par lequel elle passe.
    to_line_from_points: Tuple[str, str] # Tuple des ID des deux points définissant la droite de référence.

class DefinePerpendicularLine(BaseModel):
    """
    Définit une nouvelle ligne qui est perpendiculaire à une autre.
    Cette action est une définition pure ; pour la rendre visible, utilisez DrawLines.
    Elle se traduit directement en LaTeX par :
    \\tkzDefLine[orthogonal=through {through_point}]({p_ref1},{p_ref2})
    """
    type: Literal["def_perpendicular_line"] = "def_perpendicular_line"
    id: str                          # L'ID de notre nouvelle ligne (ex: "hauteur_A")
    through_point: str               # L'ID du point par lequel elle passe.
    to_line_from_points: Tuple[str, str] # Tuple des ID des deux points définissant la droite de référence.


# ==============================================================================
#                      MODÈLES DE CERCLES
# ==============================================================================

# --- ACTIONS DE DÉFINITION DE CERCLES ---

class DefineCircleByCenterPoint(BaseModel):
    """
    DÉFINIT un cercle à partir de son centre et d'un point par lequel il passe.
    Cette action est une définition logique, elle ne dessine rien.
    Correspond à la commande LaTeX : \\tkzDefCircle(centre, point_passant_par)
    """
    type: Literal["def_circle_by_center_point"] = "def_circle_by_center_point"
    id: str = Field(..., description="ID unique pour ce nouveau cercle (ex: 'c1').")
    center: str = Field(..., description="ID du point qui est le centre du cercle.")
    through_point: str = Field(..., description="ID du point situé sur la circonférence du cercle.")

class DefineCircleByCenterRadius(BaseModel):
    """
    DÉFINIT un cercle à partir de son centre et d'un rayon numérique.
    Cette action est une définition logique et gère la complexité de stocker
    la valeur du rayon en LaTeX.
    Correspond à : \\tkzCalcLength(...) puis \\tkzDefCircle[R](...).
    """
    type: Literal["def_circle_by_center_radius"] = "def_circle_by_center_radius"
    id: str = Field(..., description="ID unique pour ce nouveau cercle (ex: 'c_main').")
    center: str = Field(..., description="ID du point qui est le centre du cercle.")
    radius: float = Field(..., gt=0, description="Valeur numérique du rayon (doit être > 0).")

class DefineCircleByDiameter(BaseModel):
    """
    DÉFINIT un cercle à partir de deux points formant son diamètre.
    Cette action est une définition logique, elle ne dessine rien.
    Correspond à la commande LaTeX : \\tkzDefCircle[diameter](pt1, pt2)
    """
    type: Literal["def_circle_by_diameter"] = "def_circle_by_diameter"
    id: str = Field(..., description="ID unique pour ce nouveau cercle (ex: 'c_diam').")
    diameter_points: Tuple[str, str] = Field(..., description="Tuple des ID des deux points formant le diamètre.")

class DefineCircleCircumscribed(BaseModel):
    """
    DÉFINIT le cercle circonscrit à un triangle (passant par 3 points).
    Cette action est une définition logique, elle ne dessine rien.
    Correspond à la commande LaTeX : \\tkzDefCircle(pt1, pt2, pt3)
    """
    type: Literal["def_circle_circumscribed"] = "def_circle_circumscribed"
    id: str = Field(..., description="ID unique pour ce nouveau cercle (ex: 'c_circum').")
    through_points: Tuple[str, str, str] = Field(..., description="Tuple des ID des trois points par lesquels le cercle doit passer.")

class DefineCircleInscribed(BaseModel):
    """
    DÉFINIT le cercle inscrit dans un triangle (tangent aux 3 côtés).
    Cette action est une définition logique, elle ne dessine rien.
    Correspond à la commande LaTeX : \\tkzDefCircle[in](pt1, pt2, pt3)
    """
    type: Literal["def_circle_inscribed"] = "def_circle_inscribed"
    id: str = Field(..., description="ID unique pour ce nouveau cercle (ex: 'c_inscribed').")
    triangle_points: Tuple[str, str, str] = Field(..., description="Tuple des ID des trois sommets du triangle.")



# ==============================================================================
#                 MODÈLES DE RECHERCHE D'INTERSECTIONS
# ==============================================================================

# --- MODÈLE n°1 : Intersection de deux Droites ---

class FindIntersectionLineLine(BaseModel):
    """
    CALCULE et nomme le point d'intersection de deux droites.
    Chaque droite est définie par deux de ses points.
    Cette action ne dessine rien, elle ne fait que définir un nouveau point.
    Correspond à la commande LaTeX : \\tkzInterLL(p1,p2)(p3,p4)
    """
    type: Literal["find_intersection_LL"] = "find_intersection_LL"
    id: str = Field(..., description="ID unique du nouveau point d'intersection qui sera créé.")
    line1_points: Tuple[str, str] = Field(..., description="Tuple des ID des 2 points définissant la première droite.")
    line2_points: Tuple[str, str] = Field(..., description="Tuple des ID des 2 points définissant la seconde droite.")


# --- MODÈLE n°2 et n°3 : Un sous-modèle pour plus de clarté ---

class CircleDefForIntersection(BaseModel):
    """
    [Sous-modèle] Décrit un cercle pour une opération d'intersection.
    Un cercle peut être décrit soit par son centre et un point, soit par son centre et un rayon.
    Utilisez UN SEUL des deux champs.
    """
    by_center_point: Optional[Tuple[str, str]] = Field(None, description="[Mode 1] Tuple (ID du centre, ID du point sur le cercle).")
    by_center_radius: Optional[Tuple[str, float]] = Field(None, description="[Mode 2] Tuple (ID du centre, valeur du rayon).")

    @model_validator(mode='before')
    @classmethod
    def check_exclusive_fields(cls, values: Dict) -> Dict:
        """Valide qu'un seul des deux modes de définition est utilisé."""
        point_def = 'by_center_point' in values and values['by_center_point'] is not None
        radius_def = 'by_center_radius' in values and values['by_center_radius'] is not None

        if point_def and radius_def:
            raise ValueError("Ne pouvez pas définir le cercle par 'by_center_point' ET 'by_center_radius' en même temps.")
        if not point_def and not radius_def:
            raise ValueError("Vous devez définir le cercle soit via 'by_center_point', soit via 'by_center_radius'.")
        return values

# --- MODÈLE n°2 : Intersection d'une Droite et d'un Cercle ---

class FindIntersectionLineCircle(BaseModel):
    """
    CALCULE et nomme les deux points d'intersection (potentiels) d'une droite et d'un cercle.
    Même s'il n'y a qu'une ou zéro intersection, deux IDs doivent être fournis.
    Correspond à la commande LaTeX : \\tkzInterLC(ligne)(cercle)
    """
    type: Literal["find_intersection_LC"] = "find_intersection_LC"
    ids: Tuple[str, str] = Field(..., description="Tuple des IDs des deux nouveaux points à créer (ex: ['M','N']).")
    line_points: Tuple[str, str] = Field(..., description="Tuple des ID des 2 points définissant la droite.")
    circle_def: CircleDefForIntersection = Field(..., description="Description du cercle à intersecter.")


# --- MODÈLE n°3 : Intersection de deux Cercles ---

class FindIntersectionCircleCircle(BaseModel):
    """
    CALCULE et nomme les deux points d'intersection (potentiels) de deux cercles.
    Correspond à la commande LaTeX : \\tkzInterCC(cercle1)(cercle2)
    """
    type: Literal["find_intersection_CC"] = "find_intersection_CC"
    ids: Tuple[str, str] = Field(..., description="Tuple des IDs des deux nouveaux points à créer (ex: ['P','Q']).")
    circle1_def: CircleDefForIntersection = Field(..., description="Description du premier cercle.")
    circle2_def: CircleDefForIntersection = Field(..., description="Description du second cercle.")


# ==============================================================================
#                 MODÈLES DE CALCUL DE LIGNES TANGENTES AUX CERCLES
# ==============================================================================

class DefineTangentAtPointOnCircle(BaseModel):
    """
    CALCULE la ligne tangente à un cercle en un point situé SUR ce cercle.
    Cette action définit logiquement la ligne ; elle doit être dessinée avec DrawLines.
    Correspond à : \\tkzDefLine[tangent at=...](...)
    """
    type: Literal["def_tangent_at_point"] = "def_tangent_at_point"
    id: str = Field(..., description="ID de la nouvelle ligne tangente qui sera créée.")
    at_point_id: str = Field(..., description="ID du point de tangence (doit être sur le cercle).")
    circle_center_id: str = Field(..., description="ID du centre du cercle.")


class DefineTangentsFromPointToCircle(BaseModel):
    """
    CALCULE les deux lignes tangentes issues d'un point extérieur à un cercle.
    Cette action définit DEUX nouvelles lignes et DEUX nouveaux points (les points de tangence).
    """
    type: Literal["def_tangents_from_point"] = "def_tangents_from_point"
    # Les ID pour les objets que cette action va créer :
    line_ids: Tuple[str, str] = Field(..., description="Tuple des IDs des deux nouvelles lignes tangentes.")
    tangency_point_ids: Tuple[str, str] = Field(..., description="Tuple des IDs des deux nouveaux points de tangence qui seront calculés.")
    
    # Les informations sur les objets existants :
    from_point_id: str = Field(..., description="ID du point extérieur d'où partent les tangentes.")
    circle_def: CircleDefForIntersection = Field(..., description="Description du cercle cible (par centre/point ou centre/rayon).")



# --- ACTIONS DE DESSIN ---
class DrawPoints(BaseModel):
    type: Literal["draw_points"] = "draw_points"
    point_ids: List[str]
    style: Style = Field(default_factory=Style)

class DrawSegments(BaseModel): # Peut dessiner un ou plusieurs segments
    type: Literal["draw_segments"] = "draw_segments"
    segments: List[Tuple[str, str]] # ex: [["A","B"], ["B","C"]]
    arrow_spec: Optional[str] = Field(None, description="Spécification pour les flèches (ex: '->', '<->').")
    style: Style = Field(default_factory=Style)
    
class DrawLines(BaseModel): # Peut dessiner une ou plusieurs lignes
    type: Literal["draw_lines"] = "draw_lines"
    line_ids: List[str] # ex: ["d1", "mediatrice_AB"]
    style: Style = Field(default_factory=Style)

class CalculateLength(BaseModel):
    """
    CALCULE la distance entre deux points et stocke le résultat
    dans une macro LaTeX nommée.
    """
    type: Literal["calculate_length"] = "calculate_length"
    id: str = Field(..., description="ID/Nom de la nouvelle macro qui stockera la valeur de la longueur.")
    between_points: Tuple[str, str]

    @field_validator('between_points')
    @classmethod
    def check_distinct_points(cls, v: Tuple[str, str]) -> Tuple[str, str]:
        if v[0] == v[1]:
            raise ValueError("Les deux points pour un calcul de longueur doivent être distincts.")
        return v

class DrawVector(BaseModel):
    """
    [ACTION SÉMANTIQUE] DESSINE un vecteur d'un point de départ à un point d'arrivée.
    Ceci est un raccourci qui utilise en interne la commande DrawSegment avec une option de flèche.
    """
    type: Literal["draw_vector"] = "draw_vector"
    start_point_id: str = Field(..., description="ID du point d'origine du vecteur.")
    end_point_id: str = Field(..., description="ID du point de destination du vecteur.")
    style: Optional[Style] = Field(default_factory=Style)

class DrawVectorByLength(BaseModel):
    """
    [ACTION SÉMANTIQUE] DESSINE un vecteur d'un point de départ, dans la direction
    d'un autre point, mais avec une longueur spécifiée.
    """
    type: Literal["draw_vector_by_length"] = "draw_vector_by_length"
    start_point_id: str = Field(..., description="ID du point d'origine du vecteur.")
    direction_point_id: str = Field(..., description="ID du point indiquant la direction.")
    length: float = Field(..., gt=0, description="Longueur désirée du vecteur.")
    style: Optional[Style] = Field(default_factory=Style)


class DrawPolygon(BaseModel): # Remplaçons la syntaxe confuse de DrawSegments
    type: Literal["draw_polygon"] = "draw_polygon"
    point_ids: List[str] # ["A", "B", "C"] pour dessiner les côtés du triangle ABC
    style: Style = Field(default_factory=Style)


class DefineRegularPolygon(BaseModel):
    """
    DÉFINIT les sommets d'un polygone régulier. Ne dessine rien.
    Les points créés sont nommés en utilisant un préfixe.
    Par exemple, avec une base (A,B), un préfixe 'P' et 5 côtés,
    les points finaux du polygone seront accessibles via 'P1', 'P2', 'P3', 'P4', 'P5',
    où P1 et P2 sont des alias pour A et B.
    """
    type: Literal["def_regular_polygon"] = "def_regular_polygon"
    
    # ON NE DEMANDE PLUS UNE LISTE D'IDs, MAIS UN PRÉFIXE.
    name_prefix: str = Field(..., description="Le préfixe à utiliser pour nommer les sommets (ex: 'P').")
    
    from_points: Tuple[str, str] = Field(..., description="Tuple des deux points de base.")
    
    num_sides: Annotated[int, Field(gt=2)] = Field(..., description="Le nombre total de côtés du polygone.")
    
    build_method: Literal["side", "center"] = Field("side", description="Méthode de construction : 'side' ou 'center'.")
    


#  Sous-modèle pour le style des marques ---
class MarkStyle(BaseModel):
    """Détaille le style visuel d'une marque de segment."""
    mark_type: str = Field(..., description="Le type de marque à dessiner (ex: '|', '||', 's', 'o', 'z').")
    pos: Optional[float] = Field(0.5, description="Position de la marque le long du segment (de 0.0 à 1.0).")
    color: Optional[str] = None
    size: Optional[str] = Field(None, description="Taille de la marque, incluant l'unité (ex: '6pt').")
class MarkSegments(BaseModel):
    """
    DESSINE une marque visuelle sur un ou plusieurs segments.
    Principalement utilisé pour indiquer des longueurs égales.
    Correspond à la commande LaTeX : \\tkzMarkSegments
    """
    type: Literal["mark_segments"] = "mark_segments"
    on_segments: List[Tuple[str, str]] = Field(..., description="Liste des segments à marquer. Ex: [['A','B'], ['C','D']]")
    style: MarkStyle

class MarkRightAngle(BaseModel):
    type: Literal["mark_right_angle"] = "mark_right_angle"
    vertex: str
    points: Tuple[str, str]

# --- ACTION DE DESSIN DE CERCLES ---

class DrawCircles(BaseModel):
    """
    DESSINE un ou plusieurs cercles qui ont déjà été définis.
    Utilise la convention centre/point_sur_le_cercle récupérée lors de la définition.
    Correspond à la commande LaTeX : \\tkzDrawCircle(...) ou \\tkzDrawCircles(...)
    """
    type: Literal["draw_circles"] = "draw_circles"
    circle_ids: List[str] = Field(..., description="Liste des ID des cercles à dessiner.")
    style: Style = Field(default_factory=Style, description="Style de tracé appliqué aux cercles.")

class LabelCircle(BaseModel):
    """
    Place une étiquette sur un cercle.
    Le cercle est défini par son centre et un point dessus.
    """
    type: Literal["label_circle"] = "label_circle"
    center_id: str = Field(..., description="ID du centre du cercle.")
    point_on_circle_id: str = Field(..., description="ID d'un point sur le cercle pour définir le rayon.")
    angle: float = Field(90, description="Angle en degrés où placer l'étiquette (0=Est, 90=Nord).")
    label: str = Field(..., description="Le texte de l'étiquette.")
    style: Optional[Style] = Field(default_factory=Style, description="Style optionnel (ex: couleur).")

# ==============================================================================
#                 MODÈLES DE DESSIN : ELLIPSES ET DEMI-CERCLES
# ==============================================================================

class DrawEllipse(BaseModel):
    """
    DESSINE une ellipse à partir de son centre, ses axes et son angle.
    Correspond à la commande LaTeX : \\tkzDrawEllipse(centre, axe_a, axe_b, angle)
    """
    type: Literal["draw_ellipse"] = "draw_ellipse"
    center_id: str = Field(..., description="ID du point central de l'ellipse.")
    semi_major_axis: float = Field(..., gt=0, description="Longueur du demi-grand axe (> 0).")
    semi_minor_axis: float = Field(..., gt=0, description="Longueur du demi-petit axe (> 0).")
    angle: float = Field(0, description="Angle de rotation de l'ellipse en degrés (défaut: 0).")
    style: Style = Field(default_factory=Style)


class DrawSemiCircles(BaseModel):
    """
    DESSINE un ou plusieurs demi-cercles. Chaque demi-cercle est défini
    par un centre et un point sur sa circonférence.
    Correspond à : \\tkzDrawSemiCircles(centre1,pt1 centre2,pt2 ...)
    """
    type: Literal["draw_semi_circles"] = "draw_semi_circles"
    # Liste de tuples, où chaque tuple est (ID du centre, ID du point sur le cercle)
    segments: List[Tuple[str, str]] = Field(..., description="Liste des paires (centre, point) pour chaque demi-cercle.")
    style: Style = Field(default_factory=Style)

# ==============================================================================
#                      MODÈLES DE DESSIN : ARCS DE CERCLE
# ==============================================================================

class DrawArcByPoints(BaseModel):
    """
    DESSINE un arc de cercle défini par son centre et deux points (départ et arrivée).
    Correspond à la syntaxe : \\tkzDrawArc(centre,depart)(arrivee)
    """
    type: Literal["draw_arc_by_points"] = "draw_arc_by_points"
    center_id: str = Field(..., description="ID du point central de l'arc.")
    start_point_id: str = Field(..., description="ID du point de départ de l'arc.")
    end_point_id: str = Field(..., description="ID du point d'arrivée de l'arc.")
    arrow_spec: Optional[str] = Field(None, description="Spécification optionnelle pour les flèches (ex: '<->').")
    style: Style = Field(default_factory=Style)


class DrawArcByAngles(BaseModel):
    """
    DESSINE un arc de cercle défini par son centre, un rayon, et deux angles.
    Correspond à la syntaxe : \\tkzDrawArc[R](centre,rayon)(angle_dep,angle_fin)
    """
    type: Literal["draw_arc_by_angles"] = "draw_arc_by_angles"
    center_id: str = Field(..., description="ID du point central de l'arc.")
    radius: float = Field(..., gt=0, description="Valeur numérique du rayon (> 0).")
    start_angle: float = Field(..., description="Angle de départ en degrés.")
    end_angle: float = Field(..., description="Angle d'arrivée en degrés.")
    arrow_spec: Optional[str] = Field(None, description="Spécification optionnelle pour les flèches (ex: '<->').")
    style: Style = Field(default_factory=Style)

class LabelArc(BaseModel):
    """
    Place une étiquette le long d'un arc de cercle.
    L'arc est défini par trois points (départ, centre, arrivée).
    """
    type: Literal["label_arc"] = "label_arc"
    start_point_id: str = Field(..., description="ID du point de départ de l'arc.")
    center_id: str = Field(..., description="ID du centre de l'arc.")
    end_point_id: str = Field(..., description="ID du point d'arrivée de l'arc.")
    label: str = Field(..., description="Le texte de l'étiquette.")
    pos: float = Field(0.5, description="Position relative de l'étiquette le long de l'arc (0=début, 0.5=milieu, 1=fin).")
    style: Optional[Style] = Field(default_factory=Style, description="Style optionnel (ex: couleur).")


# ==============================================================================
#           MODÈLES DE CALCUL : POINTS SUR LIGNES ET CERCLES
# ==============================================================================

class DefinePointOnLine(BaseModel):
    """
    CALCULE et nomme un nouveau point situé sur une ligne à une position relative.
    Correspond à la commande LaTeX : \\tkzDefPointOnLine[pos=...](pt1,pt2)
    """
    type: Literal["def_point_on_line"] = "def_point_on_line"
    id: str = Field(..., description="ID du nouveau point qui sera créé.")
    on_line_from_points: Tuple[str, str] = Field(..., description="Tuple des 2 ID des points qui définissent la ligne.")
    pos: float = Field(..., description="Position relative sur la ligne (0=1er pt, 1=2e pt, 0.5=milieu, etc.).")


class DefinePointOnCircle(BaseModel):
    """
    CALCULE et nomme un nouveau point sur un cercle à un angle donné.
    Le rayon du cercle peut être défini soit par un point, soit par une valeur.
    """
    type: Literal["def_point_on_circle"] = "def_point_on_circle"
    id: str = Field(..., description="ID du nouveau point qui sera créé.")
    center_id: str = Field(..., description="ID du centre du cercle.")
    angle: float = Field(..., description="Angle en degrés où placer le nouveau point.")
    
    # --- Choisissez UN SEUL des deux modes de définition du rayon ---
    radius_from_point_id: Optional[str] = Field(None, description="[Mode 1] ID d'un point définissant le rayon (distance au centre).")
    radius_as_value: Optional[float] = Field(None, description="[Mode 2] Valeur numérique directe du rayon (>0).")

    @model_validator(mode='before')
    @classmethod
    def check_exclusive_radius_def(cls, values: Dict) -> Dict:
        """Valide qu'un seul des deux modes de définition du rayon est utilisé."""
        point_def = 'radius_from_point_id' in values and values['radius_from_point_id'] is not None
        value_def = 'radius_as_value' in values and values['radius_as_value'] is not None

        if point_def and value_def:
            raise ValueError("Ne pouvez pas définir le rayon avec 'radius_from_point_id' ET 'radius_as_value' en même temps.")
        if not point_def and not value_def:
            raise ValueError("Vous devez définir le rayon soit via 'radius_from_point_id', soit via 'radius_as_value'.")
        return values


# ==============================================================================
#                  MODÈLES POUR LA GESTION DES ANGLES
# ==============================================================================
class DrawAngle(BaseModel):
    """
    DESSINE les deux segments qui forment un angle.
    Ceci est un raccourci sémantique qui utilise DrawSegments en interne.
    """
    type: Literal["draw_angle"] = "draw_angle"
    
    of_angle_from_points: Tuple[str, str, str] = Field(..., description="Tuple des IDs de trois points définissant l'angle. L'ordre est important : (point_cote_1, sommet, point_cote_2).")
    
    style: Style = Field(default_factory=Style, description="Le style à appliquer aux deux segments de l'angle.")

class CalculateAngleByPoints(BaseModel):
    """
    CALCULE la valeur d'un angle défini par trois points et la stocke
    dans une macro LaTeX nommée. L'angle est mesuré de (sommet,pt1) vers (sommet,pt2).
    """
    type: Literal["calculate_angle_by_points"] = "calculate_angle_by_points"
    id: str = Field(..., description="ID/Nom de la nouvelle macro qui stockera la valeur de l'angle.")
    vertex_id: str = Field(..., description="ID du point qui est le sommet de l'angle.")
    start_point_id: str = Field(..., description="ID du point sur le premier côté de l'angle.")
    end_point_id: str = Field(..., description="ID du point sur le second côté de l'angle.")


class CalculateAngleOfSlope(BaseModel):
    """
    CALCULE la valeur de l'angle de la pente d'une droite et la stocke
    dans une macro LaTeX nommée.
    """
    type: Literal["calculate_angle_of_slope"] = "calculate_angle_of_slope"
    id: str = Field(..., description="ID/Nom de la nouvelle macro qui stockera la valeur de l'angle de pente.")
    line_points: Tuple[str, str] = Field(..., description="Tuple des 2 ID des points définissant la ligne.")

class DefineAngleBisector(BaseModel):
    """
    DÉFINIT la ligne bissectrice d'un angle donné.
    L'angle est défini par trois points. Ne dessine rien.
    Cette action doit être suivie par un 'DrawLines' pour la rendre visible.
    Correspond à : \\tkzDefLine[bisector]
    """
    type: Literal["def_angle_bisector"] = "def_angle_bisector"
    
    line_id: str = Field(..., description="ID de la nouvelle LIGNE bissectrice qui sera créée.")
    point_on_line_id: str = Field(..., description="ID du NOUVEAU POINT qui sera créé sur la ligne bissectrice.")
    
    of_angle_from_points: Tuple[str, str, str] = Field(..., description="Tuple des IDs de trois points définissant l'angle." \
    " L'ordre est important : (point_depart, sommet, point_arrivee).")

class MarkAngle(BaseModel):
    # NOTE TRES IMPORTANTE: ne jamains exposé cette solution au llm, ils doivent toujours utiliser MarkInternalAngle
    """
    DESSINE un arc pour marquer un angle. Peut aussi être rempli et/ou étiqueté.
    Cette action peut générer jusqu'à 3 commandes LaTeX (Fill, Mark, Label).
    """
    type: Literal["mark_angle"] = "mark_angle"
    vertex_id: str = Field(..., description="ID du point qui est le sommet de l'angle.")
    start_point_id: str = Field(..., description="ID du point sur le premier côté de l'angle.")
    end_point_id: str = Field(..., description="ID du point sur le second côté de l'angle.")
    label: Optional[str] = Field(None, description="Étiquette textuelle (ex: '\\alpha').")
    display_calculated_angle_id: Optional[str] = Field(None, description="ID du calcul d'angle dont la valeur doit être affichée. Exclusif avec 'label'.")
    size: float = Field(1, description="Taille de l'arc de marquage.")
    label_pos: float = Field(1.25, description="Position du label par rapport à l'arc (défaut: 1.25).")
    style: Style = Field(default_factory=Style)

    @model_validator(mode='after')
    def check_exclusive_label(self) -> 'MarkAngle':
        if self.label is not None and self.display_calculated_angle_id is not None:
            raise ValueError("Les champs 'label' et 'display_calculated_angle_id' ne peuvent pas être utilisés en même temps.")
        return self

class MarkInternalAngle(BaseModel):
    """
    [ACTION INTELLIGENTE] Dessine la marque de l'angle INTERNE.
    Détermine automatiquement le bon ordre des points pour toujours tracer l'angle
    le plus petit (< 180 degrés) entre les deux segments.
    """
    type: Literal["mark_internal_angle"] = "mark_internal_angle"
    points: Tuple[str, str, str] = Field(..., description="Tuple des 3 IDs des points (point1, sommet, point2). L'ordre n'importe pas.")
    label: Optional[str] = Field(None, description="Étiquette textuelle (ex: '\\alpha').")
    display_calculated_angle_id: Optional[str] = Field(None, description="ID du calcul d'angle dont la valeur doit être affichée. Exclusif avec 'label'.")
    size: float = Field(1, description="Taille de l'arc de marquage.")
    label_pos: float = Field(1.25, description="Position du label par rapport à l'arc.")
    style: Style = Field(default_factory=Style)

    @model_validator(mode='after')
    def check_exclusive_label(self) -> 'MarkInternalAngle':
        if self.label is not None and self.display_calculated_angle_id is not None:
            raise ValueError("Les champs 'label' et 'display_calculated_angle_id' ne peuvent pas être utilisés en même temps.")
        return self


# ==============================================================================
#                 MODÈLES DE DESSIN : SECTEURS ANGULAIRES
# ==============================================================================

class DrawAngularSectorByPoints(BaseModel):
    """
    [Secteur 1/4] DESSINE un secteur angulaire défini par son centre et deux points.
    Correspond à la commande LaTeX : \\tkzDrawSector(centre,pt_depart)(pt_arrivee)
    """
    type: Literal["draw_sector_by_points"] = "draw_sector_by_points"
    center_id: str = Field(..., description="ID du point central.")
    start_point_id: str = Field(..., description="ID du point de départ sur le cercle.")
    end_point_id: str = Field(..., description="ID du point d'arrivée sur le cercle.")
    style: Optional[Style] = Field(default_factory=Style)


class DrawAngularSectorByRotation(BaseModel):
    """
    [Secteur 2/4] DESSINE un secteur angulaire défini par son centre, un point, et un angle de rotation.
    Correspond à la commande LaTeX : \\tkzDrawSector[rotate](centre,pt_depart)(angle)
    """
    type: Literal["draw_sector_by_rotation"] = "draw_sector_by_rotation"
    center_id: str = Field(..., description="ID du point central.")
    start_point_id: str = Field(..., description="ID du point de départ sur le cercle.")
    angle: float = Field(..., description="Angle de rotation (ouverture) du secteur en degrés.")
    style: Optional[Style] = Field(default_factory=Style)


class DrawAngularSectorByAngles(BaseModel):
    """
    [Secteur 3/4] DESSINE un secteur angulaire défini par son centre, un rayon, et deux angles.
    Correspond à la commande LaTeX : \\tkzDrawSector[R](centre,rayon)(angle_dep,angle_fin)
    """
    type: Literal["draw_sector_by_angles"] = "draw_sector_by_angles"
    center_id: str = Field(..., description="ID du point central.")
    radius: float = Field(..., gt=0, description="Valeur numérique du rayon (> 0).")
    start_angle: float = Field(..., description="Angle de départ en degrés.")
    end_angle: float = Field(..., description="Angle d'arrivée en degrés.")
    style: Optional[Style] = Field(default_factory=Style)


class DrawAngularSectorByNodes(BaseModel):
    """
    [Secteur 4/4] DESSINE un secteur angulaire défini par son centre, un rayon, et deux points 'cibles'.
    L'arc s'arrête sur les rayons passant par ces deux points cibles.
    Correspond à : \\tkzDrawSector[R with nodes](centre,rayon)(cible1,cible2)
    """
    type: Literal["draw_sector_by_nodes"] = "draw_sector_by_nodes"
    center_id: str = Field(..., description="ID du point central.")
    radius: float = Field(..., gt=0, description="Valeur numérique du rayon (> 0).")
    node1_id: str = Field(..., description="ID du premier point cible définissant un rayon.")
    node2_id: str = Field(..., description="ID du second point cible définissant un rayon.")
    style: Optional[Style] = Field(default_factory=Style)


# ==============================================================================
#                 MODÈLES DE DÉFINITION DE TRIANGLES
# ==============================================================================

"""
Le triangle défini par ses angles (two angles):
Sémantique : "Construis un triangle sur le segment [AB] dont les angles en A et B sont de X et Y degrés".
Importance : Haute. C'est le cas d'usage le plus flexible et le plus général. Il permet de construire n'importe quel triangle dont on connaît la forme. Il nécessite deux paramètres : les valeurs des angles.
Le triangle équilatéral (equilateral):
Sémantique : "Construis un triangle équilatéral sur le segment [AB]".
Importance : Très haute. C'est une figure de base fondamentale.
Les triangles rectangles remarquables:
Triangle isocèle rectangle (isoceles right):
Sémantique: "Construis un triangle rectangle en C, où [AB] est l'hypoténuse".
Importance: Haute. Très commun dans les exercices (c'est un "demi-carré").
Triangle de l'écolier (school):
Sémantique: "Construis un triangle rectangle avec des angles de 30° et 60°".
Importance: Haute. C'est le fameux triangle d'équerre 30-60-90.
Triangle pythagoricien (pythagore):
Sémantique: "Construis un triangle rectangle dont les côtés sont proportionnels à 3, 4 et 5".
Importance: Haute. Le triplet pythagoricien le plus célèbre.
L'option de symétrie (swap):
Sémantique : "Construis le triangle de l'autre côté du segment [AB]".
Importance : C'est un modificateur essentiel qui s'applique à presque tous les autres types. Ce sera un simple booléen (vrai/faux) dans notre modèle.
"""
class DefineTriangleBy2Points(BaseModel):
    """
    DÉFINIT un triangle à partir d'un segment de base et d'une propriété.
    Cette action CALCULE et nomme le troisième point du triangle.
    Elle ne dessine rien.
    Correspond à la commande LaTeX : \\tkzDefTriangle(pt1,pt2)
    """
    type: Literal["def_triangle_by_2_points"] = "def_triangle_by_2_points"
    
    id: str = Field(..., description="ID du NOUVEAU point (le 3ème sommet) qui sera créé.")
    on_segment: Tuple[str, str] = Field(..., description="Tuple des ID des deux points de la base.")
    
    triangle_type: Literal[
        "equilateral", 
        "two_angles", 
        "isoceles_right", 
        "school", 
        "pythagore"
    ] = Field(..., description="Le type de triangle à construire.")

    # Champs optionnels dont la présence dépend de 'triangle_type'
    angles: Optional[Tuple[float, float]] = Field(None, description="Requis UNIQUEMENT si triangle_type est 'two_angles'. Spécifie les angles à la base (sur le segment).")
    swap: bool = Field(False, description="Si True, construit le triangle symétriquement par rapport au segment de base.")

    @model_validator(mode='after')
    def check_conditional_fields(self) -> 'DefineTriangleBy2Points':
        """
        Valide la logique conditionnelle :
        1. Le champ 'angles' DOIT être présent si triangle_type est 'two_angles'.
        2. Le champ 'angles' NE DOIT PAS être présent pour les autres types.
        """
        ttype = self.triangle_type
        has_angles = self.angles is not None

        if ttype == 'two_angles' and not has_angles:
            raise ValueError(
                "Pour un triangle de type 'two_angles', le champ 'angles' est requis."
            )
        
        if ttype != 'two_angles' and has_angles:
            raise ValueError(
                f"Le champ 'angles' n'est pas applicable pour un triangle de type '{ttype}'."
            )
            
        return self

class DefineTriangleCenter(BaseModel):
    """
    DÉFINIT un point remarquable d'un triangle (orthocentre, centre de gravité, etc.).
    Cette action CALCULE et nomme le point central demandé. Elle ne dessine rien d'autre.
    Correspond à la commande LaTeX : \\tkzDefTriangleCenter[...]
    """
    type: Literal["def_triangle_center"] = "def_triangle_center"
    
    id: str = Field(..., description="ID du NOUVEAU point remarquable qui sera créé (ex: 'H', 'G', 'O').")
    
    from_triangle_points: Tuple[str, str, str] = Field(..., description="Tuple des IDs des trois sommets du triangle de référence.")
    
    center_type: Literal[
        "orthocenter",       # Intersection des hauteurs
        "centroid",          # Intersection des médianes (centre de gravité)
        "circumcenter",      # Centre du cercle circonscrit
        "incenter",          # Centre du cercle inscrit
        "bisector_center"    # Alias pour incenter
    ] = Field(..., description="Le type de point remarquable à calculer.")


# ==============================================================================
#                 MODÈLES DE DÉFINITION DE QUADRILATÈRES
# ==============================================================================

class DefineSquare(BaseModel):
    """
    DÉFINIT les deux points manquants pour former un carré.
    Basé sur deux points de départ qui forment le premier côté.
    Ne dessine rien, ne fait que calculer les positions des nouveaux points.
    Correspond à : \\tkzDefSquare(pt1,pt2)
    """
    type: Literal["def_square"] = "def_square"
    ids: Tuple[str, str] = Field(..., description="Tuple des IDs des DEUX NOUVEAUX points qui seront créés (les 3ème et 4ème sommets).")
    from_points: Tuple[str, str] = Field(..., description="Tuple des IDs des deux points de base qui forment le premier côté du carré.")
    
class DefineRectangle(BaseModel):
    """
    DÉFINIT les deux points manquants pour former un rectangle.
    Basé sur deux points qui forment une DIAGONALE.
    Ne dessine rien, ne fait que calculer les positions des nouveaux points.
    Correspond à : \\tkzDefRectangle(pt1,pt2)
    """
    type: Literal["def_rectangle"] = "def_rectangle"
    ids: Tuple[str, str] = Field(..., description="Tuple des IDs des DEUX NOUVEAUX points qui seront créés.")
    from_diagonal: Tuple[str, str] = Field(..., description="Tuple des IDs des deux points qui forment une diagonale du rectangle.")

class DefineParallelogram(BaseModel):
    """
    DÉFINIT le point manquant pour former un parallélogramme.
    Basé sur trois points de départ.
    Ne dessine rien, ne fait que calculer la position du nouveau point.
    Correspond à : \\tkzDefParallelogram(pt1,pt2,pt3)
    """
    type: Literal["def_parallelogram"] = "def_parallelogram"
    id: str = Field(..., description="ID du NOUVEAU point (le 4ème sommet) qui sera créé.")
    from_points: Tuple[str, str, str] = Field(..., description="Tuple des IDs des trois points de base.")



class CustomLabel(BaseModel):
    """Détaille les options pour le label d'un seul point."""
    position: str                   # ex: "left", "above right". Obligatoire.
    text: Optional[str] = None      # Le texte à afficher. Si omis, l'ID du point sera utilisé.
    style: Optional[Style] = None   # Un style optionnel qui surcharge le style global pour ce point uniquement.

class LabelPoints(BaseModel):
    """
    Place les labels des points. Propose deux modes mutuellement exclusifs :
    - Mode simple ('point_ids') : Pour un placement automatique par tkz-euclide.
    - Mode personnalisé ('custom_labels') : Pour un contrôle précis de la position de chaque label.
    """
    type: Literal["label_points"] = "label_points"
    
    # === CHOISISSEZ L'UN DE CES DEUX CHAMPS ===
    point_ids: Optional[List[str]] = None
    """[Mode simple] Liste des ID des points à labelliser automatiquement."""
    
    custom_labels: Optional[Dict[str, CustomLabel]] = None
    """Dictionnaire associant un ID de point à sa position ('left', 'below', etc.)."""
    """[Mode personnalisé] Dictionnaire associant un ID de point à ses options de label."""

    style: Style = Field(default_factory=Style)

    @model_validator(mode='before')
    @classmethod
    def check_exclusive_fields(cls, values: Dict) -> Dict:
        """Valide qu'un seul des deux modes de labellisation est utilisé."""
        has_points = 'point_ids' in values and values['point_ids'] is not None
        has_custom = 'custom_labels' in values and values['custom_labels'] is not None

        if has_points and has_custom:
            raise ValueError("Ne pouvez pas utiliser 'point_ids' et 'custom_labels' en même temps. Choisissez un seul mode.")
        if not has_points and not has_custom:
            raise ValueError("Vous devez fournir soit 'point_ids' (pour un label auto) soit 'custom_labels' (pour un label personnalisé).")
        return values

# --- Sous-modèle pour les options de label ---
class LabelStyle(BaseModel):
    """Détaille les options de style et de position pour un label de segment ou de ligne."""
    position: Optional[str] = "above" # Ex: "above", "below left", etc.
    pos: Optional[float] = 0.5        # Position le long de la ligne (0.0 à 1.0 et au-delà)
    swap: bool = False                # Si True, inverse le côté du placement (utile pour les polygones)
    color: Optional[str] = None
    # On pourrait ajouter 'rotate', 'font', etc. plus tard.

# --- Le modèle pour labelliser UN segment ---
class LabelSegment(BaseModel):
    type: Literal["label_segment"] = "label_segment"
    on_segment: Tuple[str, str]   # Les deux points du segment (ex: ["A","B"])
    text: str                     # Le texte du label (ex: "5cm" ou "a")
    style: LabelStyle = Field(default_factory=LabelStyle)

# --- Le modèle pour labelliser UNE ligne ---
class LabelLine(BaseModel):
    type: Literal["label_line"] = "label_line"
    on_line: Tuple[str, str]      # Les deux points définissant la ligne (ex: ["A","B"])
    text: str                     # Le texte du label (ex: "d_1")
    style: LabelStyle = Field(default_factory=LabelStyle)
# --- A. Un nouveau sous-modèle pour structurer la nouvelle fonctionnalité ---

class DisplayCalculationParams(BaseModel):
    """Détaille comment afficher le résultat d'un calcul."""
    id_of_calculation: str = Field(..., description="L'ID du calcul (angle ou longueur) dont la valeur doit être affichée.")
    format_template: str = Field(..., description="Le modèle de texte à utiliser, avec '{}' comme emplacement pour la valeur calculée. Ex: 'La longueur est de {} cm'.")

# --- B. Le nouveau modèle DrawText ---

class DrawText(BaseModel):
    """
    Écrit un texte à des coordonnées données. Propose deux modes exclusifs :
    - Mode 'text': pour écrire une chaîne de caractères simple.
    - Mode 'display_calculation': pour afficher la valeur d'un calcul précédent.
    """
    type: Literal["draw_text"] = "draw_text"
    coords: Tuple[float, float]
    style: Optional[Style] = Field(default_factory=Style)

    # --- Choisissez UN SEUL de ces deux champs ---
    text: Optional[str] = Field(None, description="Le contenu textuel simple à afficher.")
    display_calculation: Optional[DisplayCalculationParams] = Field(None, description="Paramètres pour afficher la valeur d'un calcul.")
    
    @model_validator(mode='after')
    def check_exclusive_fields(self) -> 'DrawText':
        if self.text is not None and self.display_calculation is not None:
            raise ValueError("Les champs 'text' et 'display_calculation' ne peuvent pas être utilisés en même temps.")
        if self.text is None and self.display_calculation is None:
            raise ValueError("Vous devez fournir soit le champ 'text', soit le champ 'display_calculation'.")
        return self



# style et valeur prédéfinis de largeur de ligne
# ultra thin 0.1 pt
# very thin 0.2 pt
# thin 0.4 pt
# semithick 0.6 pt
# thick 0.8 pt
# very thick 1.2 pt
# ultra thick 1.6 pt


# === Sous-modèles techniques (non exposés directement) ===

class TranslationParams(BaseModel):
    """Paramètres pour une translation, définie par un vecteur de deux points."""
    from_point: str
    to_point: str

class HomothetyParams(BaseModel):
    """Paramètres pour une homothétie."""
    center: str
    ratio: float

class ReflectionParams(BaseModel):
    """Paramètres pour une réflexion (symétrie axiale)."""
    over_line_from_points: Tuple[str, str]

    @field_validator('over_line_from_points')
    @classmethod
    def check_distinct_points(cls, v: Tuple[str, str]) -> Tuple[str, str]:
        """Valide que les deux points définissant la droite sont différents."""
        if v[0] == v[1]:
            # Si les points sont identiques, on lève une erreur de validation claire.
            raise ValueError("Les deux points définissant une droite de réflexion doivent être distincts.")
        # Sinon, on retourne la valeur telle quelle.
        return v

class SymmetryParams(BaseModel):
    """Paramètres pour une symétrie centrale."""
    center: str

class RotationParams(BaseModel):
    """Paramètres pour une rotation."""
    center: str
    angle: float # en degrés

# class ProjectionParams(BaseModel):
#     """Paramètres pour une projection orthogonale."""
#     onto_line_from_points: Tuple[str, str]


# ==============================================================================
#                 MODÈLES DE DÉFINITION PAR TRANSFORMATION
# ==============================================================================
class DefinePointsByTransformation(BaseModel):
    """
    Modèle de base pour toutes les transformations. Contient la logique
    de validation partagée pour s'assurer que les listes d'entrée et de sortie
    ont la même taille. NE PAS UTILISER DIRECTEMENT.
    """
    new_ids: List[str]
    points_to_transform: List[str]

    @model_validator(mode='after')
    def check_list_lengths_match(self) -> 'DefinePointsByTransformation':
        if len(self.new_ids) != len(self.points_to_transform):
            raise ValueError(
                f"La liste des nouveaux IDs ({len(self.new_ids)} IDs) doit avoir "
                f"la même longueur que la liste des points à transformer ({len(self.points_to_transform)} points)."
            )
        # On vérifie aussi qu'on ne transforme pas "rien".
        if not self.points_to_transform:
             raise ValueError("La liste 'points_to_transform' ne peut pas être vide.")
        return self

# --- Maintenant, les modèles finaux héritent de cette logique ---

class DefinePointsByTranslation(DefinePointsByTransformation):
    """
    DÉFINIT un ou plusieurs points par translation.
    Calcule la position des points images, ne dessine rien.
    """
    type: Literal["def_points_by_translation"] = "def_points_by_translation"
    by: TranslationParams

class DefinePointsByHomothety(DefinePointsByTransformation):
    """DÉFINIT un ou plusieurs points par homothétie."""
    type: Literal["def_points_by_homothety"] = "def_points_by_homothety"
    by: HomothetyParams

class DefinePointsByReflection(DefinePointsByTransformation):
    """DÉFINIT un ou plusieurs points par symétrie axiale (réflexion)."""
    type: Literal["def_points_by_reflection"] = "def_points_by_reflection"
    by: ReflectionParams

class DefinePointsBySymmetry(DefinePointsByTransformation):
    """DÉFINIT un ou plusieurs points par symétrie centrale."""
    type: Literal["def_points_by_symmetry"] = "def_points_by_symmetry"
    by: SymmetryParams

class DefinePointsByRotation(DefinePointsByTransformation):
    """DÉFINIT un ou plusieurs points par rotation."""
    type: Literal["def_points_by_rotation"] = "def_points_by_rotation"
    by: RotationParams

class PatternStyle(BaseModel):
    """Sous-modèle pour le style des motifs/hachures."""
    pattern_name: Literal[
        "north east lines", 
        "north west lines", 
        "crosshatch", 
        "grid", 
        "dots"
    ] = "north east lines"
    color: str = "gray"
    pattern_thickness: Optional[Literal["thin", "thick"]] = None

class FillShapeWithPattern(BaseModel):
    """
    DESSINE et REMPLIT une forme polygonale avec un motif de hachures.
    C'est l'outil à utiliser pour représenter des plans coupés.
    """
    type: Literal["fill_shape_with_pattern"] = "fill_shape_with_pattern"
    point_ids: List[str] # ["E", "H", "C"]
    style: PatternStyle = Field(default_factory=PatternStyle)


class DefinePerspectiveCuboid(BaseModel):
    """
    [HAUT NIVEAU] Construit les 8 sommets d'un parallélépipède (cube) en perspective.
    L'utilisateur définit explicitement les 4 sommets de la base avant
    et le vecteur de translation qui donne la profondeur. Les 4 autres points sont calculés.
    """
    type: Literal["def_perspective_cuboid"] = "def_perspective_cuboid"

    base_points: Tuple[str, str, str, str] = Field(
        ...,
        description="Les noms des 4 points de la FACE AVANT, dans l'ordre anti-horaire en partant du bas à gauche. Ex: ('A','B','F','E')."
    )
    derived_points: Tuple[str, str, str, str] = Field(
        ...,
        description="Les noms des 4 points de la FACE ARRIÈRE qui seront créés, dans le même ordre. Ex: ('D','C','G','H')."
    )
    base_origin: Tuple[float, float] = Field(..., description="Coordonnées (x,y) du premier point de la base (ex: 'A').")
    base_width: float = Field(..., description="Largeur de la base (distance entre le 1er et le 2e point).")
    base_height: float = Field(..., description="Hauteur de la base (distance entre le 1er et le 4e point).")
    depth_vector: Tuple[float, float] = Field(..., description="Vecteur de translation (dx,dy) à appliquer pour obtenir la face arrière.")

# --- Union des actions possibles pour ce sprint ---
ConstructionStep = Union[
    LabelPoints,
    LabelSegment,
    LabelLine,
    LabelCircle,
    LabelArc,
    MarkRightAngle,
    MarkSegments,
    DefinePointByCoords, 
    DefineMidPoint,
    DefineLineByPoints,
    DefineParallelLine,
    DefinePerpendicularLine,
    DefineMediator,
    DrawSegments,
    DrawVector, 
    DrawVectorByLength,
    DrawLines, 
    DrawPoints, 
    DefineProjectionPoint, 
    DrawPolygon,
    DefineRegularPolygon,
    CalculateLength,
    DefineCircleByCenterPoint,
    DefineCircleByCenterRadius,
    DefineCircleByDiameter,
    DefineCircleCircumscribed,
    DefineCircleInscribed,
    DrawCircles,
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
]

# ==============================================================================
#  LE MODÈLE PRINCIPAL (Version minimale pour le Sprint 1)
# ==============================================================================

class Geometry2DInput(BaseModel):
    """
    Contrat d'entrée pour l'outil de géométrie 2D (Sprint 1).
    Focalisé sur la définition de points et le tracé de segments.
    """
    figure_config: FigureConfig = Field(default_factory=FigureConfig)
    
    # On applique la syntaxe 'Annotated' que nous avons apprise
    construction_steps: List[Annotated[ConstructionStep, Field(discriminator='type')]]

    @model_validator(mode='after')
    def check_id_dependencies(self) -> 'Geometry2DInput':
        """
        Vérifie que les objets référencés par un `id` sont définis AVANT
        d'être utilisés. C'est la garantie de la logique séquentielle.
        """
        defined_ids = set()

        for i, step in enumerate(self.construction_steps):
            step_dict = step.model_dump(exclude_unset=True)
            step_type = step_dict.get('type', '')
            
            # --- ÉTAPE 1: Identifier les NOUVEAUX IDs créés par cette étape ---
            new_ids_created = []
            
            # Champs qui créent toujours des IDs
            always_creation_keys = {'id', 'ids', 'tangency_point_id', 'tangency_point_ids',
                                    'line_id', 'new_ids', 'point_on_line_id', 'point_on_line_ids'}
            for key in always_creation_keys:
                if key in step_dict:
                    value = step_dict[key]
                    if isinstance(value, (list, tuple)):
                        new_ids_created.extend(value)
                    else:
                        new_ids_created.append(value)

            # ---  Gérer la création implicite des points du polygone ---
            if step_type == 'def_regular_polygon':
                prefix = step_dict.get('name_prefix', '')
                num_sides = step_dict.get('num_sides', 0)
                if prefix and num_sides > 0:
                    # On génère la liste des noms que LaTeX va créer (P1, P2, P3...)
                    # et on les ajoute à la liste des points créés pour cette étape.
                    implicit_ids = [f"{prefix}{k+1}" for k in range(num_sides)]
                    new_ids_created.extend(implicit_ids)

            if step_type == 'def_perspective_cuboid':
                # On lui apprend que ces deux champs créent des points.
                if 'base_points' in step_dict:
                    new_ids_created.extend(step_dict['base_points'])
                if 'derived_points' in step_dict:
                    new_ids_created.extend(step_dict['derived_points'])
            
            # Cas spécial pour line_ids : création seulement dans certains types d'étapes
            line_creation_types = {'def_tangents_from_point'}  # Ajouter d'autres types si nécessaire
            if 'line_ids' in step_dict and step_type in line_creation_types:
                line_ids = step_dict['line_ids']
                if isinstance(line_ids, (list, tuple)):
                    new_ids_created.extend(line_ids)
                else:
                    new_ids_created.append(line_ids)

            # --- ÉTAPE 2: Identifier toutes les DÉPENDANCES ---
            dependencies_to_check = []
            
            # Liste des champs de données pures (pas des IDs)
            DATA_KEYS = {'type', 'style', 'label', 'text', 'unit', 'color', 
                     'thickness', 'pattern', 'fill_color', 'position',
                     'radius', 'semi_major_axis', 'semi_minor_axis', 'angle',
                     'start_angle', 'end_angle', 'arrow_spec', 'triangle_type',
                     'center_type', 'on_segments','num_sides', 'build_method',
                     'name_prefix', 'base_points', 'derived_points',
                     'base_origin', 'base_width', 'base_height', 'depth_vector'
                     }

            for key, value in step_dict.items():
                # Ignorer les champs de données pures
                if key in DATA_KEYS:
                    continue
                    
                # Ignorer les champs de création qu'on a déjà traités
                if key in always_creation_keys:
                    continue
                if key == 'line_ids' and step_type in line_creation_types:
                    continue
                
                # Cas spécial : line_ids dans draw_lines est une DÉPENDANCE
                if key == 'line_ids' and step_type == 'draw_lines':
                    if isinstance(value, (list, tuple)):
                        dependencies_to_check.extend([item for item in value if isinstance(item, str)])
                    elif isinstance(value, str):
                        dependencies_to_check.append(value)
                    continue

                # Cas spécial : les CLÉS du dictionnaire custom_labels sont des dépendances
                if key == 'custom_labels' and isinstance(value, dict):
                    dependencies_to_check.extend(value.keys())
                    continue

                # Cas spécial : les VALEURS de circle_def sont des dépendances
                if key == 'circle_def' and isinstance(value, dict):
                    if value.get('by_center_point'):
                        dependencies_to_check.extend(value['by_center_point'])
                    if value.get('by_center_radius'):
                        # Le rayon est un float, on ne prend que la chaîne (le centre)
                        dependencies_to_check.extend([item for item in value['by_center_radius'] if isinstance(item, str)])
                    continue

                # Cas général pour tous les autres champs
                if isinstance(value, str):
                    dependencies_to_check.append(value)
                elif isinstance(value, (list, tuple)):
                    # Gérer les listes de listes comme pour les segments
                    if value and isinstance(value[0], (list, tuple)):
                        for sub_list in value:
                            dependencies_to_check.extend([item for item in sub_list if isinstance(item, str)])
                    else:
                        dependencies_to_check.extend([item for item in value if isinstance(item, str)])

            # --- ÉTAPE 3: Valider les dépendances ---
            for dep_id in set(dependencies_to_check):
                if dep_id not in defined_ids:
                    raise ValueError(
                        f"ID de dépendance non défini : '{dep_id}' est utilisé à l'étape {i+1} "
                        f"(type: '{step_type}') mais n'a pas été défini dans une étape précédente."
                    )
            
            # --- ÉTAPE 4: Enregistrer les nouveaux IDs ---
            for new_id in new_ids_created:
                if new_id in defined_ids:
                    raise ValueError(f"ID '{new_id}' redéfini à l'étape {i+1}. Les IDs doivent être uniques.")
                defined_ids.add(new_id)

        return self