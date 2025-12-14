# **Guide Opérationnel de l'Outil : `geometry_2d`**
*nom de l'outil*: `geometry_2d`

## 1. MISSION ET PHILOSOPHIE DE L'OUTIL

Cet outil génère des schémas de géométrie 2D de haute précision à partir d'une description séquentielle en JSON. Votre mission est de construire un objet `Geometry2DInput` qui est une "recette de construction" pas à pas pour la figure géométrique désirée.

La philosophie de cet outil est radicalement **constructiviste et séquentielle**. Il suit le **Paradigme "Définir, puis Dessiner"**. Pensez comme si vous résolviez un problème de géométrie sur papier :

1.  **Phase 1 : La Définition (la Réflexion)**. Vous déterminez où se trouvent les objets. "Le point M est le milieu de [AB]", "La droite (d) est la médiatrice de [BC]", "Le point I est l'intersection de (d1) et (d2)". Ce sont des actions **logiques**, des **calculs** qui ne produisent encore aucun trait. C'est l'étape `def_...` ou `find_...`.
2.  **Phase 2 : Le Dessin (l'Action)**. Une fois que tous vos objets sont mathématiquement définis, vous prenez votre crayon pour les tracer. "Je dessine le segment [AB]", "Je trace la droite (d)", "Je marque le point I". Ce sont des actions **visuelles**. C'est l'étape `draw_...`.
3.  **Phase 3 : L'Annotation (la Finition)**. Vous ajoutez les noms des points, les étiquettes et les symboles (angles droits, etc.) pour rendre la figure lisible. Ce sont les étapes `label_...` et `mark_...`.

**L'ordre de ces étapes dans votre recette est absolument crucial.** Vous devez définir un point `A` avant de pouvoir définir le milieu du segment `[AB]`. Vous devez définir une ligne `d1` avant de pouvoir la dessiner. Chaque étape s'appuie sur les précédentes.

Requis = Obligatoire dans la suite de ce guide.

NB: Si tu dois generer une image de types points dans un repere;Exemple: "dessine un repere un plan de ville et place y 4 points representant 4 quartiers ..." . Ce type de requette necessite "axes": true et "grid": true. Pour tout les autre types de generation (Exemple: 'dessine un cube ...') qui n'ont pas besoin d'un repere ou d'une grille des axes du repere, laisse ces deux champs a false pour mettre en avant ta construction principale.
### **La Clé `figure_config` : Le Cadre de votre Dessin**

Utilisez cet objet pour définir les propriétés de la toile de fond.

-   **`x_range` et `y_range` (Tuple[float, float]) :**
    -   *Mission :* Définit les limites visibles du dessin. Ex : `[-5, 5]`.
    -   *Obligatoire :* Oui, toujours fournir une estimation.

-   **`axes` et `grid` (bool) :**
    -   *Mission :* **CRUCIAL !** Contrôle l'affichage du repère et de la grille.
    -   *Règle d'or :* **Ne mets ces valeurs à `true` que si la demande en langage naturel contient explicitement ou implicitement la notion de repère, de coordonnées ou de graphe.**
    -   **Exemples :**
        -   "Dessine un **repère** orthonormé..." -> `"axes": true`
        -   "Trace le **graphe** et place les points A(2,3)..." -> `"axes": true, "grid": true`
        -   "Dessine un cube en perspective..." -> `"axes": false, "grid": false` (par défaut, on veut juste voir la figure pure).
---

## 2. STRUCTURE GÉNÉRALE DES DONNÉES

L'objet JSON que vous devez construire est composé d'une configuration de figure (`figure_config`) et d'une liste d'étapes de construction (`construction_steps`).

```json
{
  "figure_config": {
    "x_range": [-2, 8],
    "y_range": [-2, 7],
    "axes": false,
    "grid": false
  },
  "construction_steps": [
    {
      "type": "def_point_coords",
      "id": "A",
      "coords": [0, 0]
    },
    {
      "type": "def_point_coords",
      "id": "B",
      "coords": [6, 4]
    },
    {
      "type": "draw_segments",
      "segments": [["A", "B"]],
      "style": {"color": "blue"}
    },
    {
      "type": "draw_points",
      "point_ids": ["A", "B"]
    },
    {
      "type": "label_points",
      "custom_labels": {
          "A": { "position": "below left" },
          "B": { "position": "above right"}
      }
    }
  ]
}
```
 Style:
    """Définit le style visuel d'un élément."""
    color: str = "black"
    thickness: Optional[Literal["thin", "thick", "very thick"]] = None
    pattern: Optional[Literal["dashed", "dotted"]] = None
    #  AJOUTS POUR LES SURFACES 
    fill_color: Optional[str] = Field(None, description="Couleur de remplissage pour les surfaces (cercles, polygones).")
    opacity: Optional[float] = Field(None, description="Opacité du remplissage (de 0.0 à 1.0).")
---
### **3. LE DICTIONNAIRE DES BRIQUES DE CONSTRUCTION (`construction_steps`)**

La liste `construction_steps` est votre démonstration géométrique, instruction par instruction. La maîtrise de chaque brique, et surtout de leur enchaînement, est la clé pour obtenir une figure non seulement correcte, mais aussi claire et esthétique.

---
### **3.1. Les Fondations : Définir des Points**

Tout commence par les points. Ce sont les atomes de votre figure. Rien ne peut être construit sans eux.

*   #### `def_point_coords`
    *   **Mission :** Crée le point le plus fondamental qui soit : un point défini par ses coordonnées absolues dans le repère. **C'est le point de départ de 99% des figures.**
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Nom unique et sémantique pour ce point (ex: `"A"`, `"origine"`).
        *   `coords` **[Requis]** (`Tuple[float, float]`): Les coordonnées `(x, y)` du point.
        *   `label` **[Optionnel]** (`str`): Texte du label. **Note :** il est fortement recommandé d'utiliser la brique `label_points` plus tard pour un contrôle fin du positionnement.
        *   `style` **[Optionnel]** (`Style`): Pour définir la couleur ou la forme du marqueur du point s'il est dessiné.

*   #### `def_midpoint`
    *   **Mission :** Calcule et crée un nouveau point qui est le milieu d'un segment existant.
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Nom unique pour ce nouveau point milieu (ex: `"M"`, `"milieu_AB"`).
        *   `of_segment` **[Requis]** (`Tuple[str, str]`): Tuple contenant les `id` des deux points **déjà définis** qui forment le segment (ex: `["A", "B"]`). Le validateur interne s'assurera que ces IDs existent dans les étapes précédentes.

*   #### `def_projection_point`
    *   **Mission :** Calcule et crée le projeté orthogonal d'un point sur une droite existante. Très utile pour définir le pied d'une hauteur dans un triangle.
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Nom unique pour ce nouveau point projeté (ex: `"H"`, `"pied_hauteur_A"`).
        *   `from_point` **[Requis]** (`str`): L'`id` du point que l'on souhaite projeter.
        *   `on_line` **[Requis]** (`str`): L'`id` de la droite **logique** sur laquelle on projette. Cette droite doit avoir été définie au préalable (par exemple avec `def_line_by_points`).

*   #### `def_point_on_line`
    *   **Mission :** Calcule et crée un point situé sur une droite définie par deux autres points, à une position relative donnée. C'est l'outil parfait pour placer un point C sur (AB) tel que AC = 1.5 * AB ou juste placer un point sur une droite donnée.
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Nom unique du nouveau point.
        *   `on_line_from_points` **[Requis]** (`Tuple[str, str]`): Les `id` des deux points définissant la droite.
        *   `pos` **[Requis]** (`float`): La position relative. `0.0` correspond au premier point, `1.0` au second point. `0.5` est donc le milieu. Les valeurs peuvent être négatives ou supérieures à 1.

*   #### `def_point_on_circle`
    *   **Mission :** Calcule et crée un point situé sur la circonférence d'un cercle à un angle précis.
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Nom unique du nouveau point.
        *   `center_id` **[Requis]** (`str`): `id` du centre du cercle.
        *   `angle` **[Requis]** (`float`): Angle en degrés où placer le point (0° à droite, 90° en haut).
        *   **[CHOIX UNIQUE ET OBLIGATOIRE]** pour définir le rayon :
            *   `radius_from_point_id` (`str`): L'`id` d'un point sur le cercle. Le rayon sera la distance entre le centre et ce point.
            *   `radius_as_value` (`float`): Une valeur numérique directe pour le rayon.

---
### **3.2. Les Objets Linéaires : Définir des Lignes**

Une fois vos points de référence définis, vous pouvez construire des lignes. Une "ligne" au sens de l'outil est un objet géométrique infini. Ces actions ne dessinent rien ; elles **calculent et mémorisent** une droite pour une utilisation ultérieure (dessin, intersection, projection...).

CircleDefForIntersection:
    """
    [Sous-modèle] Décrit un cercle pour une opération d'intersection.
    Un cercle peut être décrit soit par son centre et un point, soit par son centre et un rayon.
    Utilisez UN SEUL des deux champs.
    """
    by_center_point: Optional[Tuple[str, str]] = Field(None, description="[Mode 1] Tuple (ID du centre, ID du point sur le cercle).")
    by_center_radius: Optional[Tuple[str, float]] = Field(None, description="[Mode 2] Tuple (ID du centre, valeur du rayon).")

    def check_exclusive_fields(cls, values: Dict) -> Dict:
        """Valide qu'un seul des deux modes de définition est utilisé."""
        point_def = 'by_center_point' in values and values['by_center_point'] is not None
        radius_def = 'by_center_radius' in values and values['by_center_radius'] is not None

        if point_def and radius_def:
            raise ValueError("Ne pouvez pas définir le cercle par 'by_center_point' ET 'by_center_radius' en même temps.")
        if not point_def and not radius_def:
            raise ValueError("Vous devez définir le cercle soit via 'by_center_point', soit via 'by_center_radius'.")
        return values
 DisplayCalculationParams:
    """Détaille comment afficher le résultat d'un calcul."""
    id_of_calculation: str = Field(..., description="L'ID du calcul (angle ou longueur) dont la valeur doit être affichée.")
    format_template: str = Field(..., description="Le modèle de texte à utiliser, avec '{}' comme emplacement pour la valeur calculée. Ex: 'La longueur est de {} cm'.")


*   #### `def_line_by_points`
    *   **Mission :** La méthode la plus fondamentale pour définir une droite : celle qui passe par deux points connus.
    *   **Note de Sagesse :** *Cette action est une déclaration pure, elle ne fait qu'associer un nom (un `id`) à une paire de points. Elle ne génère aucune sortie visible mais est essentielle pour que les autres briques (`draw_lines`, `def_projection_point`) sachent de quelle droite vous parlez.*
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Nom unique et sémantique pour cette nouvelle droite (ex: `"droite_AB"`, `"axe_x"`).
        *   `through` **[Requis]** (`Tuple[str, str]`): Tuple contenant les `id` des deux points **déjà définis** par lesquels la droite passe (ex: `["A", "B"]`).

*   #### `def_parallel_line`
    *   **Mission :** Calcule et définit une nouvelle droite passant par un point et parallèle à une droite de référence.
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Nom unique de la nouvelle droite parallèle qui sera créée (ex: `"d_parallele"`).
        *   `through_point` **[Requis]** (`str`): L'`id` du point **déjà défini** par lequel la nouvelle droite doit passer.
        *   `to_line_from_points` **[Requis]** (`Tuple[str, str]`): Tuple des `id` des deux points définissant la droite de référence.

*   #### `def_perpendicular_line`
    *   **Mission :** Calcule et définit une nouvelle droite passant par un point et perpendiculaire à une droite de référence. Idéal pour construire des hauteurs ou des repères orthogonaux.
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Nom unique de la nouvelle droite perpendiculaire (ex: `"hauteur_A"`).
        *   `through_point` **[Requis]** (`str`): L'`id` du point **déjà défini** par lequel la nouvelle droite doit passer.
        *   `to_line_from_points` **[Requis]** (`Tuple[str, str]`): Tuple des `id` des deux points définissant la droite de référence.

*   #### `def_mediator`
    *   **Mission :** Calcule et définit la médiatrice d'un segment.
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Nom unique pour cette médiatrice (ex: `"mediatrice_BC"`).
        *   `of_segment` **[Requis]** (`Tuple[str, str]`): Tuple des `id` des deux points formant le segment.

*   #### `def_angle_bisector`
    *   **Mission :** Calcule et définit la bissectrice d'un angle. C'est une brique très puissante qui crée **deux objets en une seule fois** : la droite elle-même, et un point sur cette droite pour faciliter les constructions futures.
    *   **Structure Clé :**
        *   `line_id` **[Requis]** (`str`): Le nom (`id`) que vous voulez donner à la **nouvelle droite** bissectrice.
        *   `point_on_line_id` **[Requis]** (`str`): Le nom (`id`) que vous voulez donner au **nouveau point** qui sera créé sur cette bissectrice.
        *   `of_angle_from_points` **[Requis]** (`Tuple[str, str, str]`): Tuple des `id` des trois points définissant l'angle. **L'ordre est crucial :** le sommet doit être le deuxième élément (`["point_cote_1", "sommet", "point_cote_2"]`).

*   #### `def_tangent_at_point`
    *   **Mission :** Calcule et définit la ligne tangente à un cercle en un point qui se trouve **sur** la circonférence de ce cercle.
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Le nom de la nouvelle droite tangente à créer.
        *   `at_point_id` **[Requis]** (`str`): L'`id` du point de tangence (ce point doit appartenir au cercle).
        *   `circle_center_id` **[Requis]** (`str`): L'`id` du point central du cercle(centre du cercle deja existant).

*   #### `def_tangents_from_point`
    *   **Mission :** Action avancée qui calcule et définit les **deux** droites tangentes à un cercle, issues d'un point **extérieur**. Cette brique crée au total **quatre nouveaux objets** : deux droites et deux points.
    *   **Structure Clé :**
        *   `line_ids` **[Requis]** (`Tuple[str, str]`): Tuple contenant les deux noms que vous assignez aux **deux nouvelles droites tangentes** (ex: `["t1", "t2"]`).
        *   `tangency_point_ids` **[Requis]** (`Tuple[str, str]`): Tuple contenant les deux noms que vous assignez aux **deux nouveaux points de contact** qui seront calculés par l'outil (ex: `["T1", "T2"]`).
        *   `from_point_id` **[Requis]** (`str`): L'`id` du point extérieur d'où partent les tangentes.
        *   `circle_def` **[Requis]** (`CircleDefForIntersection`): C'est un sous-objet pour décrire le cercle. Il doit contenir **soit** la clé `"by_center_point"` (un tuple `[id_centre, id_point_sur_cercle]`), **soit** la clé `"by_center_radius"` (un tuple `[id_centre, rayon]`).

---
### **3.3. Les Objets Circulaires : Définir des Cercles**

Tout comme les lignes, les cercles doivent être **définis** mathématiquement avant de pouvoir être dessinés. L'outil mémorise alors le centre et le rayon de chaque cercle défini, le rendant disponible pour des étapes ultérieures de dessin ou de calcul d'intersection.

*   #### `def_circle_by_center_point`
    *   **Mission :** La méthode de définition de cercle la plus intuitive : à partir de son centre et d'un point par lequel il doit passer.
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Nom unique et sémantique pour ce nouveau cercle (ex: `"c1"`, `"cercle_principal"`).
        *   `center` **[Requis]** (`str`): `id` du point **déjà définis** qui servira de centre .
        *   `through_point` **[Requis]** (`str`): `id` du point **déjà définis** situé sur la circonférence du cercle, qui définit donc son rayon.

*   #### `def_circle_by_center_radius`
    *   **Mission :** Définit un cercle à partir de son centre et d'une valeur numérique explicite pour son rayon.
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Nom unique pour ce nouveau cercle.
        *   `center` **[Requis]** (`str`): `id` du point qui servira de centre **déjà définis**.
        *   `radius` **[Requis]** (`float`): La longueur du rayon, qui doit être une valeur strictement positive.

*   #### `def_circle_by_diameter`
    *   **Mission :** Définit un cercle à partir de deux points qui forment l'un de ses diamètres.
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Nom unique pour ce nouveau cercle.
        *   `diameter_points` **[Requis]** (`Tuple[str, str]`): Tuple contenant les `id` des deux points **déjà définis** qui forment le diamètre.

*   #### `def_circle_circumscribed`
    *   **Mission :** Définit le cercle circonscrit à un triangle, c'est-à-dire le cercle unique passant par ses trois sommets.
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Nom unique pour ce nouveau cercle.
        *   `through_points` **[Requis]** (`Tuple[str, str, str]`): Tuple contenant les `id` des trois sommets du triangle **déjà définis**.

*   #### `def_circle_inscribed`
    *   **Mission :** Définit le cercle inscrit dans un triangle, c'est-à-dire le plus grand cercle contenu dans le triangle, tangent à ses trois côtés.
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Nom unique pour ce nouveau cercle.
        *   `triangle_points` **[Requis]** (`Tuple[str, str, str]`): Tuple contenant les `id` des trois sommets du triangle **déjà définis**.

---
### **3.4. Les Calculs : Trouver des Intersections**

Une fois que les lignes et les cercles sont définis, vous pouvez les utiliser pour en calculer les points d'intersection. Ces actions, tout comme les précédentes, ne dessinent rien. Leur unique mission est de **créer et nommer** de nouveaux points qui deviendront disponibles pour les étapes suivantes de la construction.

*   #### `find_intersection_LL`
    *   **Mission :** Trouve et nomme le point d'intersection unique (s'il existe) entre deux droites distinctes.
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Nom unique que vous donnez au **nouveau point d'intersection** qui sera créé.
        *   `line1_points` **[Requis]** (`Tuple[str, str]`): Tuple des `id` de 2 points définissant la première droite.
        *   `line2_points` **[Requis]** (`Tuple[str, str]`): Tuple des `id` de 2 points définissant la seconde droite.

*   #### `find_intersection_LC`
    *   **Mission :** Trouve et nomme les points d'intersection (jusqu'à deux) entre une droite et un cercle.
    *   **Note cruciale :** Vous devez **toujours** fournir deux `id` pour les nouveaux points, même si vous prévoyez qu'il n'y aura qu'un seul point de tangence ou aucune intersection.
    *   **Structure Clé :**
        *   `ids` **[Requis]** (`Tuple[str, str]`): Tuple contenant les deux noms que vous assignez aux **nouveaux points** qui seront créés (ex: `["M", "N"]`).
        *   `line_points` **[Requis]** (`Tuple[str, str]`): Tuple des `id` de 2 points définissant la droite.
        *   `circle_def` **[Requis]** (`CircleDefForIntersection`): C'est le même sous-objet vu précédemment. Il permet de décrire le cercle à intersecter en utilisant **soit** la clé `"by_center_point"` (`[id_centre, id_point_sur_cercle]`), **soit** la clé `"by_center_radius"` (`[id_centre, rayon]`). EX: "circle1_def": {"by_center_point": ["A", "D"]},

*   #### `find_intersection_CC`
    *   **Mission :** Trouve et nomme les points d'intersection (jusqu'à deux) entre deux cercles.
    *   **Note cruciale :** Tout comme pour `find_intersection_LC`, vous devez **toujours** fournir deux `id` pour les nouveaux points.
    *   **Structure Clé :**
        *   `ids` **[Requis]** (`Tuple[str, str]`): Tuple contenant les deux noms que vous assignez aux **nouveaux points** qui seront créés (ex: `["P", "Q"]`).
        *   `circle1_def` **[Requis]** (`CircleDefForIntersection`): Description du premier cercle (par centre/point ou centre/rayon).
        *   `circle2_def` **[Requis]** (`CircleDefForIntersection`): Description du second cercle (par centre/point ou centre/rayon).

---
---
### **3.5. Les Formes Composites : Définir des Triangles et Polygones**

Ces briques sont des "constructeurs" avancés. Leur mission est de calculer et créer plusieurs points à la fois pour former des polygones spécifiques, vous évitant ainsi de laborieux calculs manuels de coordonnées ou d'intersections. Ce sont des actions de **définition** : elles créent de nouveaux points mais ne les relient pas encore visuellement.

*   #### `def_triangle_by_2_points`
    *   **Mission :** Crée le troisième sommet d'un triangle à partir d'un segment de base et d'une propriété géométrique spécifique. C'est l'une des briques les plus puissantes pour construire des figures complexes rapidement.
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Le nom (`id`) que vous donnez au **nouveau point (le 3ème sommet)** qui sera calculé.
        *   `on_segment` **[Requis]** (`Tuple[str, str]`): Tuple des `id` des deux points formant le segment de base.
        *   `triangle_type` **[Requis]** (`"equilateral"` | `"two_angles"` | `"isoceles_right"` | `"school"` | `"pythagore"`): Le type de triangle à construire.
            *   `equilateral` : Triangle équilatéral.
            *   `isoceles_right` : Triangle rectangle isocèle (demi-carré), où le segment de base est l'hypoténuse.
            *   `school` : Triangle rectangle avec angles de 30° et 60°.
            *   `pythagore` : Triangle rectangle dont les côtés sont proportionnels à 3, 4 et 5.
            *   `two_angles` : Le cas le plus général. Vous spécifiez les deux angles à la base.
        *   `angles` **[Conditionnel]** (`Tuple[float, float]`): Requis **uniquement si `triangle_type` est `"two_angles"`**. Fournit les valeurs en degrés des angles sur le segment de base.
        *   `swap` **[Optionnel]** (`bool`, défaut: `false`): Si `true`, construit le triangle de l'autre côté du segment de base (symétriquement).

*   #### `def_regular_polygon`
    *   **Mission :** Définit et crée tous les sommets d'un polygone régulier à partir d'un côté initial. L'outil nomme automatiquement les points pour vous.
    *   **Note Sémantique Importante :** *Cette action ne vous demande pas une liste d'IDs à créer. Elle prend un préfixe et s'occupe du reste. Si vous fournissez les points de base "A" et "B" et le préfixe "P", l'outil créera les points `P1`, `P2`, `P3`... où `P1` sera un alias pour "A" et `P2` un alias pour "B".*
    *   **Structure Clé :**
        *   `name_prefix` **[Requis]** (`str`): Le préfixe qui sera utilisé pour nommer tous les sommets (ex: `"P"`).
        *   `from_points` **[Requis]** (`Tuple[str, str]`): Tuple des deux points de base définissant le premier côté du polygone.
        *   `num_sides` **[Requis]** (`int`, `>2`): Le nombre total de côtés du polygone (ex: `5` pour un pentagone).

*   #### `def_square`
    *   **Mission :** Crée les deux sommets manquants pour former un carré, à partir d'un côté initial.
    *   **Structure Clé :**
        *   `ids` **[Requis]** (`Tuple[str, str]`): Tuple des noms que vous donnez aux **deux nouveaux sommets** qui seront créés (3ème et 4ème).
        *   `from_points` **[Requis]** (`Tuple[str, str]`): Tuple des `id` des deux points de base qui forment le premier côté du carré.

*   #### `def_rectangle`
    *   **Mission :** Crée les deux sommets manquants d'un rectangle, à partir de ses **deux sommets opposés (une diagonale)**.
    *   **Structure Clé :**
        *   `ids` **[Requis]** (`Tuple[str, str]`): Tuple des noms que vous donnez aux **deux nouveaux sommets** qui seront créés.
        *   `from_diagonal` **[Requis]** (`Tuple[str, str]`): Tuple des `id` des deux points qui forment une diagonale.

*   #### `def_parallelogram`
    *   **Mission :** Crée le quatrième et dernier sommet d'un parallélogramme à partir de trois sommets consécutifs.
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Le nom que vous donnez au **quatrième sommet** qui sera créé.
        *   `from_points` **[Requis]** (`Tuple[str, str, str]`): Tuple des `id` des trois premiers sommets, dans l'ordre.

*   #### `def_triangle_center`
    *   **Mission :** Calcule et crée un des points remarquables d'un triangle.
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Le nom conventionnel du point à créer (ex: `"G"` pour le centre de gravité, `"O"` pour le centre du cercle circonscrit).
        *   `from_triangle_points` **[Requis]** (`Tuple[str, str, str]`): Les `id` des trois sommets du triangle de référence.
        *   `center_type` **[Requis]** (`"orthocenter"` | `"centroid"` | `"circumcenter"` | `"incenter"`| "bisector_center"): Le type de point remarquable à calculer.
            *   `orthocenter` : Intersection des hauteurs.
            *   `centroid` : Intersection des médianes (centre de gravité).
            *   `circumcenter` : Centre du cercle circonscrit (identique au résultat de `def_circle_circumscribed`).
            *   `incenter` : Centre du cercle inscrit (identique au résultat de `def_circle_inscribed`).
                 "bisector_center": Centre des bissectrices des 3 angles aux somments du triangles.

---
### **3.6. Le Dessin : Rendre les Objets Visibles**

Les briques de cette section sont les "crayons" de l'outil. Elles prennent les `id` des objets que vous avez définis (points, lignes, cercles...) et les tracent sur la figure. C'est aussi à cette étape que vous appliquez le style visuel (couleur, épaisseur, remplissage...).

*   #### `draw_points`
    *   **Mission :** Dessine une marque visible (généralement un petit cercle) aux emplacements de points déjà définis.
    *   **Structure Clé :**
        *   `point_ids` **[Requis]** (`List[str]`): Une liste des `id` de tous les points que vous souhaitez rendre visibles.
        *   `style` **[Optionnel]** (`Style`): Pour contrôler la couleur (`color`) ou d'autres attributs visuels des points.

*   #### `draw_segments`
    *   **Mission :** Dessine un ou plusieurs segments de droite (traits finis) en reliant des paires de points. C'est la brique la plus commune pour dessiner les côtés d'un polygone après avoir défini ses sommets.
    *   **Structure Clé :**
        *   `segments` **[Requis]** (`List[Tuple[str, str]]`): Une **liste de paires** d'`id` de points. Chaque paire représente un segment à tracer. Par exemple : `[["A", "B"], ["B", "C"]]` pour dessiner les segments [AB] et [BC].
        *   `arrow_spec` **[Optionnel]** (`str`): Ajoute des flèches aux segments. Utilisez des chaînes de caractères comme `->`, `<-`, `<->` ou encore `-|` (pour une terminaison en barre).
        *   `style` **[Optionnel]** (`Style`): Pour contrôler la couleur (`color`), l'épaisseur (`thickness`) et le motif (`pattern`) des segments.

*   #### `draw_vector`
    *   **Mission :** Un raccourci sémantique pour dessiner un vecteur. En réalité, cette brique est une simplification de `draw_segments` avec une flèche (`arrow_spec: "->"`).
    *   **Structure Clé :**
        *   `start_point_id` **[Requis]** (`str`): `id` du point d'origine du vecteur.
        *   `end_point_id` **[Requis]** (`str`): `id` du point de destination du vecteur.
        *   `style` **[Optionnel]** (`Style`).

*   #### `draw_lines`
    *   **Mission :** Dessine des droites infinies (qui s'étendent jusqu'aux bords de la figure). Cette brique va chercher dans la "mémoire" de l'outil les droites que vous avez précédemment créées avec les actions `def_line_...`, `def_mediator`, `def_parallel_line`, etc.
    *   **Structure Clé :**
        *   `line_ids` **[Requis]** (`List[str]`): Une liste des `id` de toutes les droites que vous souhaitez dessiner.
        *   `style` **[Optionnel]** (`Style`).

*   #### `draw_polygon`
    *   **Mission :** Raccourci efficace pour dessiner les côtés d'un polygone. L'outil reliera les points dans l'ordre fourni et fermera la forme en reliant le dernier point au premier.
    *   **Structure Clé :**
        *   `point_ids` **[Requis]** (`List[str]`): Liste ordonnée des `id` des sommets du polygone (ex: `["A", "B", "C"]`).
        *   `style` **[Optionnel]** (`Style`): Contrôle l'apparence des arêtes. Utilisez également `fill_color` et `opacity` ici pour remplir le polygone.

*   #### `draw_circles`
    *   **Mission :** Dessine un ou plusieurs cercles qui ont été préalablement définis avec l'une des actions `def_circle_...`.
    *   **Structure Clé :**
        *   `circle_ids` **[Requis]** (`List[str]`): Une liste des `id` des cercles que vous souhaitez rendre visibles.
        *   `style` **[Optionnel]** (`Style`): Pour la couleur (`color`), le motif (`pattern`) du trait, mais aussi la couleur de remplissage (`fill_color`) et la transparence (`opacity`).

*   #### `draw_angle`
    *   **Mission :** Raccourci sémantique pour dessiner les deux segments qui forment un angle. Il s'agit d'une commodité qui évite d'utiliser `draw_segments` pour `[point1, sommet]` puis `[sommet, point2]`.
    *   **Structure Clé :**
        *   `of_angle_from_points` **[Requis]** (`Tuple[str, str, str]`): Les trois points définissant l'angle. L'ordre `[point_côté_1, sommet, point_côté_2]` est important.
        *   `style` **[Optionnel]** (`Style`): Le style à appliquer aux deux segments.

*   #### `draw_text`
    *   **Mission :** Affiche un texte libre à une position absolue dans la figure. Peut afficher du texte simple ou, plus puissamment, le résultat d'un calcul (longueur, angle).
    *   **Structure Clé :**
        *   `coords` **[Requis]** (`Tuple[float, float]`): Coordonnées `(x, y)` où placer le texte.
        *   **[CHOIX UNIQUE ET OBLIGATOIRE]** pour le contenu :
            *   `text` (`str`): Le texte littéral à afficher (ex: `"Figure 1"`).
            *   OU
            *   `display_calculation` (`DisplayCalculationParams`): Un sous-objet pour afficher le résultat d'un calcul.
                *   `id_of_calculation` **[Requis]** (`str`): L'`id` du calcul (`calculate_length` ou `calculate_angle...`) à afficher.
                *   `format_template` **[Requis]** (`str`): Un modèle de texte avec `{}` où la valeur sera insérée (ex: `"La longueur AB est de {} cm"`).
        *   `style` **[Optionnel]** (`Style`): Principalement pour la `color`.

---
---

### **3.7. Le Dessin d'Arcs et de Formes Circulaires Partielles**

Cette section couvre les outils spécifiques pour dessiner des portions de cercles ou d'ellipses. Ces briques sont toutes des actions de dessin directes et proposent différentes manières de définir la forme souhaitée.

*   #### `draw_arc_by_points`
    *   **Mission :** La méthode la plus courante pour dessiner un arc de cercle : en spécifiant son centre, un point de départ et un point d'arrivée. L'arc est tracé dans le sens anti-horaire.
    *   **Structure Clé :**
        *   `center_id` **[Requis]** (`str`): `id` du centre de l'arc.
        *   `start_point_id` **[Requis]** (`str`): `id` du point où l'arc commence.
        *   `end_point_id` **[Requis]** (`str`): `id` du point où l'arc se termine.
        *   `arrow_spec` **[Optionnel]** (`str`): Spécification pour les flèches (ex: `'<->'` , `'->'`, `'<-'`).
        *   `style` **[Optionnel]** (`Style`).

*   #### `draw_arc_by_angles`
    *   **Mission :** Dessine un arc de cercle à partir d'un centre, d'un rayon numérique, et de deux angles (départ et arrivée).
    *   **Structure Clé :**
        *   `center_id` **[Requis]** (`str`): `id` du centre de l'arc.
        *   `radius` **[Requis]** (`float`, `>0`): Valeur numérique du rayon.
        *   `start_angle` **[Requis]** (`float`): Angle de départ en degrés.
        *   `end_angle` **[Requis]** (`float`): Angle d'arrivée en degrés.
        *   `arrow_spec` **[Optionnel]** (`str`).
        *   `style` **[Optionnel]** (`Style`).

*   #### `draw_semi_circles`
    *   **Mission :** Dessine un ou plusieurs demi-cercles. Chaque demi-cercle est défini par les deux points formant son diamètre.
    *   **Structure Clé :**
        *   `segments` **[Requis]** (`List[Tuple[str, str]]`): Une liste de paires de points. Chaque paire `[A, B]` définit un diamètre pour un demi-cercle à tracer.
        *   `style` **[Optionnel]** (`Style`).

*   #### `draw_ellipse`
    *   **Mission :** Dessine une ellipse complète.
    *   **Structure Clé :**
        *   `center_id` **[Requis]** (`str`): `id` du point central de l'ellipse.
        *   `semi_major_axis` **[Requis]** (`float`, `>0`): Longueur du demi-grand axe.
        *   `semi_minor_axis` **[Requis]** (`float`, `>0`): Longueur du demi-petit axe.
        *   `angle` **[Optionnel]** (`float`, défaut: `0`): Angle de rotation de l'ellipse en degrés.
        *   `style` **[Optionnel]** (`Style`): Utilisez `fill_color` et `opacity` pour un remplissage.

---
### **3.8. Le Dessin de Secteurs Angulaires**

Un secteur angulaire est une portion de disque ("une part de camembert"). Il est défini par un centre, un rayon et un angle. Toutes ces actions permettent de dessiner et surtout de **remplir** ces portions.

*   #### `draw_sector_by_points`
    *   **Mission :** Dessine le plus petit secteur angulaire défini par un centre et deux points sur la circonférence.
    *   **Structure Clé :**
        *   `center_id` **[Requis]** (`str`).
        *   `start_point_id` **[Requis]** (`str`).
        *   `end_point_id` **[Requis]** (`str`).
        *   `style` **[Optionnel]** (`Style`): **Essentiel ici**, utilisez `fill_color` et `opacity` pour le remplissage.

*   #### `draw_sector_by_rotation`
    *   **Mission :** Dessine un secteur en faisant "tourner" un point de départ d'un certain angle autour du centre.
    *   **Structure Clé :**
        *   `center_id` **[Requis]** (`str`).
        *   `start_point_id` **[Requis]** (`str`).
        *   `angle` **[Requis]** (`float`): Angle d'ouverture du secteur en degrés.
        *   `style` **[Optionnel]** (`Style`).

*   #### `draw_sector_by_angles`
    *   **Mission :** Dessine un secteur à partir d'un rayon numérique et de deux angles.
    *   **Structure Clé :**
        *   `center_id` **[Requis]** (`str`).
        *   `radius` **[Requis]** (`float`, `>0`).
        *   `start_angle` **[Requis]** (`float`).
        *   `end_angle` **[Requis]** (`float`).
        *   `style` **[Optionnel]** (`Style`).

*   #### `draw_sector_by_nodes`
    *   **Mission :** Une méthode plus avancée où l'arc du secteur est contraint par un rayon donné, mais s'arrête sur les droites passant par le centre et deux "points cibles" (nodes).
    En claire, DESSINE un secteur angulaire défini par son centre, un rayon, et deux points 'cibles'.
    L'arc s'arrête sur les rayons passant par ces deux points cibles.
    *   **Structure Clé :**
        *   `center_id` **[Requis]** (`str`).
        *   `radius` **[Requis]** (`float`, `>0`).
        *   `node1_id` **[Requis]** (`str`): Le premier point cible définissant une direction.
        *   `node2_id` **[Requis]** (`str`): Le second point cible.
        *   `style` **[Optionnel]** (`Style`).

---
### **3.9. Les Annotations : Labelliser et Marquer**

Une fois tous vos objets définis et dessinés, cette dernière passe consiste à ajouter les étiquettes (labels) et les marques symboliques (angles droits, segments égaux) qui donnent son sens à la figure.

*   #### `label_points`
    *   **Mission :** Place les noms des points sur la figure. C'est la brique d'annotation la plus essentielle. Elle propose deux modes d'utilisation qui s'excluent mutuellement.
    *   **Structure Clé :**
        *   **[CHOIX UNIQUE]** pour le mode de placement :
            *   `point_ids` (`List[str]`): **Mode simple**. Vous donnez une liste d'IDs des points deja definis que vous souhaites labeliser, et l'outil tente de placer les labels automatiquement pour éviter les collisions. Efficace pour les cas simples.
            *   OU
            *   `custom_labels` (`Dict[str, CustomLabel]`): **Mode de précision**. C'est votre outil le plus puissant pour une lisibilité parfaite. C'est un dictionnaire python où chaque clé est l' `id` d'un point, et la valeur est un sous-objet `CustomLabel` décrivant le placement.
                *   `position` **[Requis]** (`str`): La position du label par rapport au point. Les valeurs possibles sont `"left"`, `"right"`, `"above"`, `"below"`, et leurs combinaisons comme `"above left"`, `"below right"`.
                *   `text` **[Optionnel]** (`str`): Pour surcharger le texte du label. Si omis, l' `id` du point est utilisé.
        *   `style` **[Optionnel]** (`Style`): Style global appliqué à tous les labels (principalement la `color`).
        NOTE: Il est recommendé fortement d'utiliser `custom_labels` pour ameliorer la lisibilité d'un dessin geometrique.

*   #### `label_segment` / `label_line`
    *   **Mission :** Place une étiquette de texte (par exemple une longueur ou un nom) le long d'un segment ou d'une ligne.
    *   **Structure Clé :**
        *   `on_segment` ou `on_line` **[Requis]** (`Tuple[str, str]`): Les deux points qui définissent l'objet à étiqueter.
        *   `text` **[Requis]** (`str`): Le texte à afficher (ex: `"5cm"`, `"a"`,`"(AB)"`pour une droite, `"[AB]"` pour un segment, `"d_1"` ou encore `"L=3cm"`). Le texte sera automatiquement mis en forme mathématique.
        *   `style` **[Optionnel]** (`LabelStyle`): Un sous-objet pour un contrôle fin.
            *   `position` (`str`): `"above"`, `"below"`, `"left"` etc. pour placer l'étiquette par rapport à la ligne.
            *   `pos` (`float`, défaut: `0.5`): Position *le long* de la ligne (0.0 au début, 0.5 au milieu, 1.0 à la fin).
            *   `swap` (`bool`): Inverse le côté du placement (de "above" à "below").

*   #### `label_circle` / `label_arc`
    *   **Mission :** Place une étiquette sur la circonférence d'un cercle ou le long d'un arc.
    *   **Structure Clé :**
        *   Pour `label_circle` : `center_id` et `point_on_circle_id` **[Requis]**, et un `angle` en degrés pour la position.
        *   Pour `label_arc` : `start_point_id`, `center_id`, `end_point_id` **[Requis]**, et `pos` (`float` de 0 à 1) pour la position le long de l'arc.
        *   Dans les deux cas, `label` (`str`) est **requis** pour le texte.

*   #### `mark_right_angle`
    *   **Mission :** Dessine le symbole canonique de l'angle droit (un petit carré).
    *   **Structure Clé :**
        *   `vertex` **[Requis]** (`str`): L'`id` du sommet de l'angle droit.
        *   `points` **[Requis]** (`Tuple[str, str]`): Tuple des `id` des deux autres points formant l'angle. L'angle droit sera marqué entre `(point1, vertex)` et `(point2, vertex)`.

*   #### `mark_segments`
    *   **Mission :** Dessine une marque symbolique sur un ou plusieurs segments, typiquement pour indiquer qu'ils ont la même longueur.
    *   **Structure Clé :**
        *   `on_segments` **[Requis]** (`List[Tuple[str, str]]`): La liste des segments à marquer (ex: `[["A","B"], ["C","D"]]`).
        *   `style` **[Requis]** (`MarkStyle`): Un sous-objet de style spécifique aux marques.
            *   `mark_type` **[Requis]** (`str`): Le symbole à dessiner. Les valeurs communes sont `|`, `||`, `|||` (barres), `s` (petit slash), `o` (petit cercle), `x`.
            *   `pos` **[Optionnel]** (`float`, défaut `0.5`): Position de la marque le long du segment.

*   #### `mark_internal_angle`
    *   **Mission :** **[ACTION INTELLIGENTE]** La méthode **privilégiée** pour marquer et étiqueter des angles. Elle dessine un arc pour indiquer un angle et détermine automatiquement le sens de tracé pour toujours marquer l'angle interne (< 180°). C'est la brique à utiliser dans 99% des cas.
    *   **Structure Clé :**
        *   `points` **[Requis]** (`Tuple[str, str, str]`): Les 3 points de l'angle (`[pt1, sommet, pt2]`). Grâce à l'intelligence de l'outil, l'ordre de `pt1` et `pt2` n'a pas d'importance.
        *   **[CHOIX UNIQUE]** pour le label :
            *   `label` (`str`): Pour un label textuel direct (ex: `\\alpha`, `\\beta`).
            *   OU
            *   `display_calculated_angle_id` (`str`): `id` d'un calcul d'angle (`calculate_angle_by_points`) dont la valeur numérique doit être affichée.
        *   `size` **[Optionnel]** (`float`, défaut `1`): Taille/rayon de l'arc de marquage.
        *   `label_pos` **[Optionnel]** (`float`, défaut `1.25`): Distance du label par rapport à l'arc.
        *   `style` **[Optionnel]** (`Style`): Pour la couleur du trait (`color`), mais aussi et surtout le remplissage (`fill_color`, `opacity`).

*   #### `fill_shape_with_pattern`
    *   **Mission :** Remplit une forme polygonale fermée avec un motif de hachures. À utiliser pour les plans, les aires, etc.
    *   **Structure Clé :**
        *   `type`: "fill_shape_with_pattern"
        *   `point_ids` **[Requis]** (`List[str]`): Liste des sommets du polygone à hachurer.
        *   `style` **[Optionnel]** (`PatternStyle`): Objet pour contrôler le style des hachures.
            *   `pattern_name` (`str`): Le type de hachures ("north east lines", 
        "north west lines", 
        "crosshatch", 
        "grid", 
        "dots").
            *   `color` (`str`): La couleur des lignes de hachurage.
---

### **3.10. Calculs et Transformations Avancées et dessins avancées**

Les briques de cette section se divisent en deux catégories : celles qui **extraient des mesures** de la figure, et celles qui **créent de nouveaux points** par transformation géométrique.

---
#### **Les Calculs de Mesures**

Ces actions ne créent aucun objet visible. Leur unique but est de calculer une valeur numérique (longueur ou angle) et de la stocker dans une "variable" interne, prête à être affichée plus tard avec les briques `draw_text` ou `mark_internal_angle`.

*   #### `calculate_length`
    *   **Mission :** Calcule la distance entre deux points et mémorise le résultat.
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Nom de la "variable" qui stockera la valeur de la longueur (ex: `"longueur_AB"`). C'est cet `id` que vous utiliserez dans `display_calculation`.
        *   `between_points` **[Requis]** (`Tuple[str, str]`): Les `id` des deux points entre lesquels mesurer la distance.

*   #### `calculate_angle_by_points`
    *   **Mission :** Calcule la valeur d'un angle défini par trois points et la mémorise.
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Nom de la "variable" qui stockera la valeur de l'angle (ex: `"valeur_angle_A"`).
        *   `vertex_id` **[Requis]** (`str`): `id` du point sommet de l'angle.
        *   `start_point_id` **[Requis]** (`str`): `id` d'un point sur le premier côté.
        *   `end_point_id` **[Requis]** (`str`): `id` d'un point sur le second côté. L'angle est mesuré dans le sens anti-horaire de (sommet-start) vers (sommet-end).

*   #### `calculate_angle_of_slope`
    *   **Mission :** Calcule l'angle de la pente d'une droite par rapport à l'horizontale.
    *   **Structure Clé :**
        *   `id` **[Requis]** (`str`): Nom de la "variable" qui stockera l'angle de pente.
        *   `line_points` **[Requis]** (`Tuple[str, str]`): Tuple des `id` des deux points définissant la droite.

---
#### **Les Transformations Géométriques**

Ces briques sont des constructeurs de points extrêmement puissants. Elles prennent une liste de points existants et créent leurs images par une transformation géométrique, vous évitant ainsi tout calcul. Toutes ces actions partagent une structure commune.
**Ces outils sont la puissance meme du catalogue pour reussir a dessiner des figures comme des pyramides, cubes,cylindres....**

**Structure Commune des Transformations (`def_points_by_...`)** :
*   `type` : `"def_points_by_translation"`, `"def_points_by_rotation"`, etc.
*   `points_to_transform` **[Requis]** (`List[str]`): La liste des `id` des points que vous voulez transformer.
*   `new_ids` **[Requis]** (`List[str]`): La liste des `id` que vous donnez aux **nouveaux points images** qui seront créés. **Cette liste doit impérativement avoir la même taille que `points_to_transform`**.
*   `by` **[Requis]** (`...Params`): Un sous-objet décrivant la transformation elle-même. C'est cet objet qui change pour chaque type de transformation.

---
*   #### `def_points_by_translation`
    *   **Mission :** Crée l'image d'un ou plusieurs points par la translation définie par un vecteur (un point de départ et un point d'arrivée).
    *   **Paramètres `by` (`TranslationParams`) :**
        *   `from_point` **[Requis]** (`str`): `id` du point de départ du vecteur de translation.
        *   `to_point` **[Requis]** (`str`): `id` du point d'arrivée du vecteur de translation.

        EX: {
            "type": "def_points_by_translation",
            "points_to_transform": ["A", "B", "C"],
            "new_ids": ["A_t", "B_t", "C_t"],
            "by": { "from_point": "B", "to_point": "O" }
        },

*   #### `def_points_by_rotation`
    *   **Mission :** Crée l'image de points par une rotation autour d'un centre et d'un angle donné.
    *   **Paramètres `by` (`RotationParams`) :**
        *   `center` **[Requis]** (`str`): `id` du centre de rotation.
        *   `angle` **[Requis]** (`float`): Angle de rotation en degrés.

*   #### `def_points_by_homothety`
    *   **Mission :** Crée l'image de points par une homothétie (agrandissement/réduction).
    *   **Paramètres `by` (`HomothetyParams`) :**
        *   `center` **[Requis]** (`str`): `id` du centre de l'homothétie.
        *   `ratio` **[Requis]** (`float`): Le rapport de l'homothétie (peut être négatif).

*   #### `def_points_by_symmetry`
    *   **Mission :** Crée l'image de points par une symétrie centrale.
    *   **Paramètres `by` (`SymmetryParams`) :**
        *   `center` **[Requis]** (`str`): `id` du point qui est le centre de symétrie.

*   #### `def_points_by_reflection`
    *   **Mission :** Crée l'image de points par une symétrie axiale (réflexion par rapport à une droite).
    *   **Paramètres `by` (`ReflectionParams`) :**
        *   `over_line_from_points` **[Requis]** (`Tuple[str, str]`): Tuple des deux `id` de points qui définissent l'axe de symétrie.

<!--
#### **`def_perspective_cuboid` (OUTIL DE CONSTRUCTION DE "BOÎTES" 3D)**

*   **MISSION (Le Pourquoi) :**
    Cette brique est votre constructeur "magique" pour dessiner des formes en 3D comme des boîtes, des dés, ou des bâtiments (des cubes et des parallélépipèdes) de manière **parfaite et prévisible à chaque fois.**
    Oubliez le placement manuel des 8 sommets. Vous définissez la face avant et la profondeur, et l'outil calcule la face arrière pour vous.

*   **Philosophie :** C'est un processus en 2 temps :
    1.  Vous décrivez la face avant comme un simple rectangle sur votre feuille.
    2.  Vous donnez un ordre de "décalage" (le vecteur de profondeur) pour créer la face arrière.

*   **Structure des Paramètres :**
    *   `base_points` (`Tuple[str, str, str, str]`) : **[IMPORTANT]** Les **noms** que vous choisissez pour les 4 sommets de la **face avant**. L'ordre est crucial : commencez en bas à gauche et tournez dans le sens anti-horaire (par convention : `("A", "B", "F", "E")`).
    *   `derived_points` (`Tuple[str, str, str, str]`) : **[IMPORTANT]** Les **noms** que vous choisissez pour les 4 sommets de la **face arrière** qui seront créés, dans le même ordre (par convention : `("D", "C", "G", "H")`).
    *   `base_origin` (`Tuple[float, float]`) : Les coordonnées du **premier point** de la base (le `A` de `base_points`).
    *   `base_width` (`float`) : La largeur de la face avant (distance entre `A` et `B`).
    *   `base_height` (`float`) : La hauteur de la face avant (distance entre `A` et `E`).
    *   `depth_vector` (`Tuple[float, float]`) : Le décalage `(dx, dy)` pour créer la face arrière. C'est le vecteur `A` -> `D`.

*   **Exemple de Traduction :**
    > **Commande :** "Dessine un cube ABCDEFGH, de côté 5, avec l'origine A en (0,0)."
    >
    > **Traduction en JSON :**
    > ```json
    > {
    >   "type": "def_perspective_cuboid",
    >   "base_points": ["A", "B", "F", "E"],
    >   "derived_points": ["D", "C", "G", "H"],
    >   "base_origin": [0, 0],
    >   "base_width": 5,
    >   "base_height": 5,
    >   "depth_vector": [2, 2]
    > }
    > ```
    > *(Après cette brique, les 8 points A, B, C, D, E, F, G, H existent tous avec les bonnes coordonnées pour une perspective parfaite, et sont prêts à être utilisés pour le dessin des arêtes et le hachurage.)*
-->
---
## 4. Règle d'Or : La Séquence est TOUT

Ce principe est le plus important de tous et ne souffre **aucune exception**. L'outil traite votre liste de `construction_steps` dans l'ordre, comme une recette de cuisine. La violation de cette règle est la source d'erreur la plus commune.

> **Un objet (point, droite, cercle...) doit être DÉFINI dans une étape `N` avant que son `id` puisse être utilisé comme référence (dans `on_segment`, `through_point`, `circle_ids`, `point_ids`, etc.) dans une étape `M`, où `M > N`.**

Par exemple, la séquence suivante est **INVALIDE** et provoquera une erreur :
```json
// SÉQUENCE INCORRECTE !
"construction_steps": [
    // ERREUR: L'outil ne connaît pas encore "A" ou "B"
    { "type": "draw_segments", "segments": [["A", "B"]] }, 
    
    // Les définitions arrivent TROP TARD
    { "type": "def_point_coords", "id": "A", "coords": [0, 0] },
    { "type": "def_point_coords", "id": "B", "coords": [4, 4] }
]
```
La seule séquence **VALIDE** est :
```json
// SÉQUENCE CORRECTE
"construction_steps": [
    // 1. DÉFINIR les prérequis
    { "type": "def_point_coords", "id": "A", "coords": [0, 0] },
    { "type": "def_point_coords", "id": "B", "coords": [4, 4] },

    // 2. UTILISER les objets définis
    { "type": "draw_segments", "segments": [["A", "B"]] }
]
```
**Pensez toujours dans l'ordre logique de la géométrie :**
*Voici le suite de pensée pour vous non negociable*
**Définition Points → Définition Lignes/Cercles → Calculs/Transformations → Dessins → Annotations.**

---

## 5. Guide du Style : Votre Art pour la Clarté Visuelle

Un schéma géométriquement juste mais visuellement confus est un schéma raté. Le paramètre `style` présent dans la plupart des briques est votre palette pour garantir la lisibilité. Il se présente toujours sous la forme d'un objet JSON.

Voici l'ensemble des options de style que vous pouvez utiliser. Toutes sont optionnelles.

#### **Détail du sous-objet `Style`**

*   `color`
    *   **Description :** La couleur du trait pour les lignes/polygones, des points, ou du texte.
    *   **Valeur :** `str` (ex: `"black"`, `"red"`, `"blue"`).

*   `thickness`
    *   **Description :** Épaisseur du trait.
    *   **Valeur :** `str` ex: | `"thin"` | `"thick"` | `"very thick"`.
    *   **Note technique :** *Ces valeurs sont des alias pour des épaisseurs précises : `thin` (0.4pt), `thick` (0.8pt), `very thick` (1.2pt).*

*   `pattern`
    *   **Description :** Le style du trait (continu, tirets, pointillés). Defaut=None (continu).
    *   **Valeur :** `str` ex: | `"dashed"` | `"dotted"`.

*   `fill_color`
    *   **Description :** Couleur de remplissage. **Pertinent uniquement** pour les formes fermées (`draw_polygon`, `draw_circles`, les secteurs `draw_sector...`, `draw_ellipse`, et les marques d'angle `mark_internal_angle`).
    *   **Valeur :** `str` (ex: `"red"`, `"blue"`).

*   `opacity`
    *   **Description :** Niveau de transparence du remplissage (`fill_color`). Très utile pour les superpositions. `0.0` est totalement transparent, `1.0` est totalement opaque.
    *   **Valeur :** `float` (de `0.0` à `1.0`, ex: `0.2`).

#### **Exemple d'application de `style`**
```json
"construction_steps": [
    // ... définir les points A, B, C ...
    {
        "type": "draw_polygon",
        "point_ids": ["A", "B", "C"],
        "style": {
            "color": "blue",              // Le contour du triangle sera bleu
            "thickness": "very thick",    // avec un trait très épais
            "fill_color": "blue",         // L'intérieur sera aussi rempli en bleu
            "opacity": 0.15               // mais de manière très transparente
        }
    }
]
```
> ### **PÉCHÉS CAPITAUX (Erreurs entraînant un Échec Garanti)**
>
> 1.  **Le Péché d'Imbrication :** NE JAMAIS définir un objet à l'intérieur d'un autre(jamains de def... dans un autre def...). Chaque objet (point, ligne...) doit être créé dans sa propre étape de `construction_steps` avant d'être utilisé par son `id` dans une étape ultérieure.
> 2.  **Le Péché de l'ID Inconnu :** NE JAMAIS utiliser un `id` dans un champ comme `from_point`, `attach_to_id`, etc., si cet `id` n'a pas été défini dans une étape précédente de la liste `construction_steps`. La séquence est cruciale.
> 3.  **la logique du dessin final :** Une figure mathematique ou artistique doit avoir une certaine logique attendu par l'oeil humain pour appreciation. Par exemple : les faces et les lignes cachées dans une perpective(pattern),la superposition ds figures(opacité), le positionnement des labels(custom_labels), etiquettage des longueurs, des veteurs ...etc
---
## 6. Démarche de Réflexion & Exemples (Thought Process & Exemples)

La clé pour maîtriser cet outil n'est pas de connaître chaque brique par cœur, mais de savoir **les assembler dans un ordre logique**. Cette section vous apprend à penser comme l'outil : "Définir d'abord, dessiner ensuite". Chaque exemple est décomposé en deux temps : **le plan de pensée** (la stratégie) et **l'écriture du JSON** (l'exécution).

### **Exemple 1 : Le B.A.-BA — La Médiatrice d'un Segment**

C'est l'exercice le plus fondamental, qui illustre parfaitement le paradigme "Définir puis Dessiner".

*   #### **Étape 1 : Le Plan (Pensée)**
    > **Ma Mission :** Dessiner la médiatrice du segment [AB].
    >
    > **Comment je dois penser ?** Je dois décomposer le problème dans l'ordre où un mathématicien le construirait à la règle et au compas.
    >
    > 1.  **Prérequis : De quoi ai-je besoin ?** D'un segment [AB]. Pour avoir un segment, il me faut deux points, A et B. L'action la plus simple pour cela est `def_point_coords`. Ce sera ma toute première étape.
    > 2.  **La Construction : Quels objets dois-je définir ?** La médiatrice est une droite. L'outil propose une brique spécifique pour cela : `def_mediator`. Je vais donc l'utiliser. Je pourrais aussi vouloir marquer le milieu du segment, M. La brique `def_midpoint` est parfaite pour ça.
    > 3.  **La Visualisation : Qu'est-ce que je veux voir à la fin ?**
        *   Je veux voir le segment [AB] lui-même. J'utiliserai donc `draw_segments`.
        *   Je veux voir la médiatrice, que j'ai logiquement nommée. J'utiliserai `draw_lines`. Je peux lui donner un style (rouge, en pointillés) pour la distinguer.
        *   Je veux voir les points A, B, et M. Je les dessinerai avec `draw_points`.
        *   Enfin, pour la clarté, je dois afficher leurs noms. J'utiliserai `label_points`.

    > **Ma séquence est donc claire :** `def_point_coords` (pour A, B) → `def_midpoint` (pour M) → `def_mediator` (pour la droite) → `draw_segments` → `draw_lines` → `draw_points` → `label_points`. L'ordre des actions de dessin à la fin a peu d'importance, mais il est plus propre de tout définir d'abord.

*   #### **Étape 2 : L'Écriture du JSON (Action)**

    ```json
    {
        "figure_config": { "x_range": [-2, 8], "y_range": [-2, 8],"axes": false, "grid": false}
        "construction_steps": [
            // === PHASE 1: DÉFINITION DE TOUS LES OBJETS MATHÉMATIQUES ===
            { "type": "def_point_coords", "id": "A", "coords": [0, 0] },
            { "type": "def_point_coords", "id": "B", "coords": [6, 4] },
            { "type": "def_midpoint", "id": "M", "of_segment": ["A", "B"] },
            { "type": "def_mediator", "id": "medAB", "of_segment": ["A", "B"] },
            
            // === PHASE 2: DESSIN ET ANNOTATION DE TOUT CE QUI EST VISIBLE ===
            { "type": "draw_segments", "segments": [["A", "B"]] },
            { "type": "draw_lines", "line_ids": ["medAB"], "style": {"color": "red", "pattern": "dashed"} },
            { "type": "draw_points", "point_ids": ["A", "B", "M"] },
            { "type": "label_points", "custom_labels": {
                "A": {"position": "below left"},
                "B": {"position": "above right"},
                "M": {"position": "below"}
            }}
        ]
    }
    ```

### **Exemple 2 : Construire avec des Parallèles et Perpendiculaires**

Cet exemple montre comment définir des droites non pas par leurs points, mais par leurs *propriétés* par rapport à d'autres droites.

*   #### **Étape 1 : Le Plan (Pensée)**
    > **Ma Mission :** Tracer une droite (d1) passant par A et B, puis tracer une parallèle à (d1) passant par un point C, et une perpendiculaire à (d1) passant aussi par C.
    >
    > **Comment je dois penser ?**
    >
    > 1.  **Les Fondations :** Il me faut des points. Je vais créer A, B, et C avec `def_point_coords`. C'est la base.
    > 2.  **La Référence :** Mes deux nouvelles droites dépendent d'une droite de référence, (AB). Bien que je puisse la définir implicitement dans les prochaines étapes, la philosophie de l'outil est d'être explicite. Mais pour ce cas, les briques `def_parallel_line` et `def_perpendicular_line` n'ont pas besoin que la droite (AB) ait un `id`, elles ont juste besoin des *points* 'A' et 'B'. Je peux donc passer directement à la définition des nouvelles droites. Je dois aussi marquer l'angle droit pour montrer la perpendicularité.
    > 3.  **Les Définitions Clés :**
        *   Pour la parallèle, la brique `def_parallel_line` est faite pour ça. Je lui donnerai l'`id` "par_C". Elle a besoin du point `C` et de la référence `["A", "B"]`.
        *   Pour la perpendiculaire, j'utilise `def_perpendicular_line`. Je lui donnerai l'id "perp_C" et les mêmes informations de construction.
        *   Je veux marquer l'angle droit en C : `mark_right_angle`. Le sommet est C, les deux autres points sont A et B.
    > 4.  **La Visualisation :** Je dois tout rendre visible pour vérifier ma construction.
        *   Le segment de référence [AB] : `draw_segments`.
        *   La parallèle : `draw_lines` avec l'`id` "par_C".
        *   La perpendiculaire : `draw_lines` avec l'`id` "perp_C".
        *   Les points A, B, C : `draw_points` et `label_points`.

    > **Séquence Logique :** `def_point_coords` (A,B,C) → `def_parallel_line` → `def_perpendicular_line` → `draw_segments` → `draw_lines`→ `mark_right_angle` →  `draw_points` → `label_points`.

*   #### **Étape 2 : L'Écriture du JSON (Action)**
    ```json
    {
        "figure_config": { "x_range": [-2, 8], "y_range": [-2, 8] },
        "construction_steps": [
            // === PHASE 1: DÉFINITIONS ===
            { "type": "def_point_coords", "id": "A", "coords": [0, 1] },
            { "type": "def_point_coords", "id": "B", "coords": [7, 3] },
            { "type": "def_point_coords", "id": "C", "coords": [1, 5] },
            
            // On définit la parallèle. C'est une action logique, rien n'est dessiné.
            {
                "type": "def_parallel_line", 
                "id": "par_C",
                "to_line_from_points": ["A", "B"], 
                "through_point": "C"
            },
            // On définit la perpendiculaire.
            {
                "type": "def_perpendicular_line", 
                "id": "perp_C", 
                "to_line_from_points": ["A", "B"], 
                "through_point": "C"
            },
            
            // === PHASE 2: DESSIN ===
            { "type": "draw_segments", "segments": [["A", "B"]], "style": {"color": "blue"} }, 
            { "type": "draw_lines", "line_ids": ["par_C"], "style": {"color": "green", "pattern": "dashed"} },
            { "type": "draw_lines", "line_ids": ["perp_C"], "style": {"color": "red"} },
            { "type": "mark_right_angle", "vertex": "C", "points": ["A", "B"] },
            { "type": "draw_points", "point_ids": ["A", "B", "C"] },
            { "type": "label_points", "point_ids": ["A", "B", "C"] }
        ]
    }
    ```

### **Exemple 3 : Construire avec un Support Invisible — La Hauteur d'un Triangle**

C'est un cas d'usage plus subtil mais extrêmement puissant. Il montre comment on peut utiliser un objet défini *logiquement* sans jamais le dessiner, juste pour servir de support à une autre construction.

*   #### **Étape 1 : Le Plan (Pensée)**
    > **Ma Mission :** Dessiner le triangle ABC et la hauteur issue de A.
    >
    > **Comment je dois penser ?**
    >
    > 1.  **Les Sommets :** Un triangle a besoin de 3 sommets. Je commence donc par `def_point_coords` pour A, B, et C.
    > 2.  **La Hauteur - La Logique :** La hauteur issue de A est le segment [AH], où H est le projeté orthogonal de A sur la droite (BC).
    > 3.  **Le Problème :** Pour *projeter* le point A, j'ai besoin de la *droite* (BC), pas juste du segment [BC]. Le segment [BC] a une fin, mais la droite (BC) est infinie et sert de support à la projection.
    > 4.  **La Solution Constructiviste :** Je dois **définir la droite (BC)** en tant qu'objet logique. La brique `def_line_by_points` est parfaite pour ça. Je lui donnerai l'`id` "droite_BC". **Je n'ai pas besoin de la dessiner**, j'ai juste besoin qu'elle existe dans la mémoire de l'outil.
    > 5.  **La Construction de H :** Maintenant que "droite_BC" existe, je peux l'utiliser. La brique `def_projection_point` me permet de créer H en projetant A sur "droite_BC".
    > 6.  **La Visualisation :**
        *   Je veux voir le triangle : `draw_polygon` avec les points A, B, C.
        *   Je veux voir la hauteur, qui est le **segment** [AH] : `draw_segments`. Je vais la mettre en pointillés bleus pour la distinguer.
        *   Je veux marquer l'angle droit en H : `mark_right_angle`. Le sommet est H, les deux autres points sont A et B (ou C, peu importe car ils sont sur la même droite).
        *   Enfin, je dessine et j'étiquette tous les points (A, B, C et le nouveau H).

    > **Ma séquence est limpide :** `def_point_coords` (A,B,C) → `def_line_by_points` (pour créer la référence invisible "droite_BC") → `def_projection_point` (pour créer H) → `draw_polygon` → `draw_segments` (pour la hauteur) → `mark_right_angle` → `draw_points` → `label_points`.

*   #### **Étape 2 : L'Écriture du JSON (Action)**
    ```json
    {
        "figure_config": { "x_range": [-1, 7], "y_range": [-1, 5] },
        "construction_steps": [
            // === PHASE 1: DÉFINITIONS ===
            { "type": "def_point_coords", "id": "A", "coords": [0, 0] },
            { "type": "def_point_coords", "id": "B", "coords": [6, 0] },
            { "type": "def_point_coords", "id": "C", "coords": [3, 4] }, 
            
            // L'étape cruciale : définir la droite (BC) comme un objet logique invisible.
            { "type": "def_line_by_points", "id": "droite_BC", "through": ["B", "C"] },
            
            // Maintenant que "droite_BC" existe, on peut l'utiliser pour définir H.
            { "type": "def_projection_point", "id": "H", "from_point": "A", "on_line": "droite_BC" },
            
            // === PHASE 2: DESSIN ET ANNOTATIONS ===
            { "type": "draw_polygon", "point_ids": ["A", "B", "C"] }, 
            { "type": "draw_segments", "segments": [["A", "H"]], "style": {"color": "blue", "pattern": "dotted"} }, 
            { "type": "mark_right_angle", "vertex": "H", "points": ["A", "B"] },
            { "type": "draw_points", "point_ids": ["A", "B", "C", "H"] },
            { "type": "label_points", "point_ids": ["A", "B", "C", "H"] }
        ]
    }
    ```
---

### **Exemple 4 : La Magie des Cercles et Intersections en Chaîne**

Cet exemple est l'épreuve du feu. Il montre comment résoudre un problème complexe en le décomposant en une chaîne séquentielle d'actions simples où la sortie de l'une devient l'entrée de la suivante.

*   #### **Étape 1 : Le Plan (Pensée)**
    > **Ma Mission :** Construire une figure complexe impliquant deux cercles et deux droites qui s'intersectent de multiples fois.
    >
    > **Comment je dois penser ?** Surtout, ne pas paniquer. Je dois rester fidèle à ma philosophie "Définir puis Dessiner" et avancer pas à pas, comme un ordinateur. Ma question doit toujours être : "Pour définir cet objet, quels objets doivent déjà exister ?".
    >
    > 1.  **Les Fondations :** La toile de fond. Je vois deux droites (AB) et (CD). Pour les définir, j'ai besoin de quatre points. Ma première action est donc de définir A, B, C, et D avec `def_point_coords`.
    > 2.  **L'Échafaudage :** Pour pouvoir utiliser les droites et les dessiner, je les définis logiquement avec `def_line_by_points`, en leur donnant les `id` "d1" et "d2".
    > 3.  **Le Premier Calcul :** Je peux maintenant définir mon premier point calculé : le point I, intersection de (AB) et (CD). La brique `find_intersection_LL` est faite pour ça. Elle a besoin des points (A,B) et (C,D), que j'ai déjà. **À cet instant, `I` existe.**
    > 4.  **Le Premier Cercle :** Je vois un cercle (c1) centré en A et passant par D. La brique `def_circle_by_center_point` est idéale. A et D existent déjà, donc je peux définir "c1". **Maintenant, `c1` existe.**
    > 5.  **Le Deuxième Calcul :** L'énoncé demande de trouver les intersections de la droite (CD) (définie par les points C,D) et du cercle (c1) (défini par A,D). La brique `find_intersection_LC` est parfaite. J'ai tous les éléments. Elle va me créer les points M et N. **À cet instant, M et N existent.**
    > 6.  **Le Deuxième Cercle - la réaction en chaîne :** Le cercle (c2) est centré en B et passe par M, un des points que je viens *juste* de créer. C'est ici que la séquence est critique. Comme M existe, je peux maintenant définir (c2) avec `def_circle_by_center_point`. **Maintenant, `c2` existe.**
    > 7.  **Le Troisième Calcul :** Je peux enfin trouver P et Q, l'intersection des cercles (c1) et (c2). J'utilise `find_intersection_CC`. Comme (c1) et (c2) sont tous deux définis, je peux le faire. **Maintenant, P et Q existent.**
    > 8.  **La Phase Finale : Dessin et Lisibilité.** La partie "Définition" est terminée. Tous mes points (A,B,C,D,I,M,N,P,Q) et objets (d1,d2,c1,c2) sont connus de l'outil.
        *   Je vais dessiner les lignes et les cercles en premier (`draw_lines`, `draw_circles`) pour poser le décor.
        *   Ensuite, je vais dessiner les points. **Astuce de Pro :** Je dessine les points de base (A,B,C,D) en noir, et les points calculés (I,M,N,P,Q) en rouge pour bien montrer le résultat de ma construction.
        *   Enfin, le coup de grâce pour la clarté : `label_points` avec l'option `custom_labels`. Je prends le temps de placer chaque label (`above`, `below left`...) pour qu'il n'y ait aucune ambiguïté.

    > Ce raisonnement a transformé un problème intimidant en une liste d'étapes simples et garanties correctes.

*   #### **Étape 2 : L'Écriture du JSON (Action)**
    ```json
    {
        "figure_config": { "x_range": [-2, 12], "y_range": [-2, 10] },
        "construction_steps": [
            // === PHASE 1: DÉFINITIONS SÉQUENTIELLES ===
            // 1. Points de base
            {"type": "def_point_coords", "id": "A", "coords": [0, 2]},
            {"type": "def_point_coords", "id": "B", "coords": [8, 4]},
            {"type": "def_point_coords", "id": "C", "coords": [2, 8]},
            {"type": "def_point_coords", "id": "D", "coords": [6, 0]},
            // 2. Définition logique des lignes
            {"type": "def_line_by_points", "id": "d1", "through": ["A", "B"]},
            {"type": "def_line_by_points", "id": "d2", "through": ["C", "D"]},
            // 3. Calcul de 'I' (dépend de A,B,C,D)
            {"type": "find_intersection_LL", "id": "I", "line1_points": ["A", "B"], "line2_points": ["C", "D"]},
            // 4. Définition du cercle 'c1' (dépend de A,D)
            {"type": "def_circle_by_center_point", "id": "c1", "center": "A", "through_point": "D"},
            // 5. Calcul de 'M','N' (dépend de C,D et 'c1')
            {"type": "find_intersection_LC", "ids": ["M", "N"], "line_points": ["C", "D"], "circle_def": {"by_center_point": ["A", "D"]}},
            // 6. Définition du cercle 'c2' (dépend de B et du nouveau point 'M')
            {"type": "def_circle_by_center_point", "id": "c2", "center": "B", "through_point": "M"},
            // 7. Calcul de 'P','Q' (dépend de 'c1' et 'c2')
            {"type": "find_intersection_CC", "ids": ["P", "Q"], "circle1_def": {"by_center_point": ["A", "D"]}, "circle2_def": {"by_center_point": ["B", "M"]}},
            
            // === PHASE 2: DESSIN ET ANNOTATIONS ===
            {"type": "draw_lines", "line_ids": ["d1", "d2"], "style": {"color": "gray"}},
            {"type": "draw_circles", "circle_ids": ["c1", "c2"], "style": {"color": "blue", "pattern": "dotted"}},
            {"type": "draw_points", "point_ids": ["A", "B", "C", "D"]},
            {"type": "draw_points", "point_ids": ["I", "M", "N", "P", "Q"], "style": {"color": "red"}},
            {"type": "label_points", "custom_labels": {
                "A": {"position": "left"}, "B": {"position": "right"}, "C": {"position": "above"}, "D": {"position": "right"},
                "I": {"position": "below"}, "N": {"position": "above left"}, "M": {"position": "above right"},
                "P": {"position": "above right"}, "Q": {"position": "below right"}
            }}
        ]
    }
    ```
---

### **Exemple 5 : Polygones Réguliers et Affichage de Mesures**

Cet exemple illustre un gain de temps massif. Au lieu de tout construire, on demande à l'outil de le faire pour nous. Puis on lui demande d'analyser sa propre création.

*   #### **Étape 1 : Le Plan (Pensée)**
    > **Ma Mission :** Dessiner un pentagone régulier basé sur un segment [AB], puis calculer et afficher la longueur d'une de ses diagonales.
    >
    > **Comment je dois penser ?**
    >
    > 1.  **La Base :** Tout polygone régulier est construit sur un premier côté. J'ai donc besoin de deux points, A et B. `def_point_coords` est la brique qu'il me faut.
    > 2.  **L'Automatisation :** Construire un pentagone régulier à la main est un enfer. Heureusement, il y a la brique `def_regular_polygon`.
        *   **La question clé :** Comment vais-je nommer les points ? La brique ne me demande pas des `id`. Elle me demande un `name_prefix`. C'est une astuce de l'outil. Je vais choisir le préfixe "P".
        *   **Comment j'utilise les points créés ?** Je dois lire attentivement le guide : "Si je donne le préfixe 'P', les points créés seront 'P1', 'P2', 'P3', 'P4', 'P5'". Je dois m'en souvenir pour les étapes suivantes.
    > 3.  **L'Analyse :** Je veux la longueur d'une diagonale, par exemple celle reliant le 3ème et le 5ème sommet (P3 et P5).
        *   Je dois d'abord **calculer** cette longueur. La brique `calculate_length` est là pour ça. Elle prend les points `["P3", "P5"]` (que je sais exister grâce à l'étape précédente) et stocke le résultat dans une variable. Je nommerai cette variable "longueur_diag".
        *   **Maintenant, je veux afficher ce résultat.** La brique `draw_text` est parfaite. Elle a un mode spécial `display_calculation`. Je vais l'utiliser pour dire : "Affiche le contenu de la variable 'longueur_diag' dans un joli texte à une certaine coordonnée".
    > 4.  **La Visualisation :**
        *   Pour voir le pentagone, le plus simple est `draw_polygon`, en lui fournissant la liste des points que je connais : `["P1", "P2", "P3", "P4", "P5"]`.
        *   Je dessinerai et labelliserai les points pour m'assurer que tout est correct.
    >
    > **La Stratégie est simple :** Je définis les fondations, je lance le "constructeur automatique", j'analyse son résultat avec les outils de calcul, puis je dessine et j'annote tout.

*   #### **Étape 2 : L'Écriture du JSON (Action)**
    ```json
    {
        "figure_config": { "x_range": [-1, 7], "y_range": [-1, 7] },
        "construction_steps": [
            // === PHASE 1: DÉFINITION AUTOMATISÉE ===
            {"type": "def_point_coords", "id": "A", "coords": [1, 1]},
            {"type": "def_point_coords", "id": "B", "coords": [4, 1]},
            {
                "type": "def_regular_polygon",
                "num_sides": 5,
                "from_points": ["A", "B"],
                "name_prefix": "P" 
            },

            // === PHASE 2: CALCUL ET ANALYSE ===
            // On calcule la longueur entre P3 et P5 (créés à l'étape précédente)
            {
                "type": "calculate_length",
                "id": "longueurP3P5",
                "between_points": ["P3", "P5"]
            },
            
            // === PHASE 3: DESSIN ET AFFICHAGE ===
            { "type": "draw_polygon", "point_ids": ["P1", "P2", "P3", "P4", "P5"] },
            // On affiche le résultat du calcul
            {
                "type": "draw_text",
                "coords": [3, 6],
                "display_calculation": {
                    "id_of_calculation": "longueurP3P5",
                    "format_template": "P3P5 = {} cm"
                }
            },
            {"type": "draw_points", "point_ids": ["P1", "P2", "P3", "P4", "P5"]},
            {"type": "label_points", "point_ids": ["P1", "P2", "P3", "P4", "P5"]}
        ]
    }
    ```

### **Exemple 6 : L'Art des Transformations Géométriques**

Cet exemple illustre une philosophie de construction totalement différente, non pas basée sur les coordonnées, mais sur la transformation d'une forme existante.

*   #### **Étape 1 : Le Plan (Pensée)**
    > **Ma Mission :** Dessiner un triangle ABC, puis dessiner son image par une rotation et son image par une translation.
    >
    > **Comment je dois penser ?** C'est un processus en couches. Je crée ma "scène" initiale, puis j'ajoute des "calques" avec les transformations.
    >
    > 1.  **La Scène Initiale (Le Modèle) :** Je dois d'abord avoir quelque chose à transformer. Je vais donc créer un triangle de base ABC. J'aurai aussi besoin de points de référence pour mes transformations (un centre de rotation O, des points pour le vecteur de translation). Donc, la première étape est une série de `def_point_coords` pour A, B, C, O, etc. Pour la clarté, je dessine immédiatement ce triangle initial, par exemple en gris fin, pour montrer qu'il s'agit de la forme "d'origine".
    > 2.  **Première Transformation : La Rotation.**
        *   Je veux créer l'image du triangle ABC. La brique à utiliser est `def_points_by_rotation`.
        *   **Entrée :** Je dois lui donner la liste des points à transformer : `["A", "B", "C"]`.
        *   **Sortie :** Je dois lui dire comment nommer les nouveaux points créés : `["A_r", "B_r", "C_r"]`. La correspondance se fait dans l'ordre.
        *   **Paramètres :** La transformation a besoin d'un centre (le point `O`) et d'un `angle`.
        *   **Résultat :** Après cette étape, les points `A_r`, `B_r`, `C_r` existent et je peux les utiliser.
    > 3.  **Deuxième Transformation : La Translation.**
        *   Même logique. J'utilise `def_points_by_translation`.
        *   **Entrée :** Je re-transforme ma figure de base `["A", "B", "C"]`.
        *   **Sortie :** Je nomme les nouvelles images `["A_t", "B_t", "C_t"]`.
        *   **Paramètres :** La translation a besoin d'un vecteur, défini par un point de départ et un point d'arrivée. J'ai défini des points pour cela.
        *   **Résultat :** Les points `A_t`, `B_t`, `C_t` existent maintenant aussi.
    > 4.  **Visualisation Finale :** La phase de définition est terminée, j'ai 9 points au total.
        *   J'ai déjà dessiné le triangle de base.
        *   Je vais maintenant dessiner le triangle tourné (`A_r, B_r, C_r`) avec `draw_polygon` et une couleur vive, comme le bleu.
        *   Puis, je dessine le triangle translaté (`A_t, B_t, C_t`) avec une autre couleur, comme le vert.
        *   Enfin, je labellise tous les points avec `label_points` pour une compréhension parfaite.

    > La pensée ici n'est pas "où est A' ?" mais "comment A' est-il obtenu à partir de A ?". Je décris le *processus* de transformation à l'outil.

*   #### **Étape 2 : L'Écriture du JSON (Action)**
    ```json
    {
        "figure_config": { "x_range": [-2, 12], "y_range": [-2, 10] },
        "construction_steps": [
            // === PHASE 1: DÉFINITION DE LA SCÈNE INITIALE ===
            { "type": "def_point_coords", "id": "A", "coords": [0, 1] },
            { "type": "def_point_coords", "id": "B", "coords": [3, 0] },
            { "type": "def_point_coords", "id": "C", "coords": [2, 3] },
            { "type": "def_point_coords", "id": "O", "coords": [5, 5] }, // Centre de rotation
            { "type": "def_point_coords", "id": "V1", "coords": [0,0] }, // Origine vecteur translation
            { "type": "def_point_coords", "id": "V2", "coords": [8,1] }, // Destination vecteur
            { "type": "draw_polygon", "point_ids": ["A", "B", "C"], "style": {"color": "gray", "pattern": "dashed"} },
            
            // === PHASE 2: DÉFINITION DES NOUVEAUX POINTS PAR TRANSFORMATION ===
            {
                "type": "def_points_by_rotation",
                "points_to_transform": ["A", "B", "C"],
                "new_ids": ["A_r", "B_r", "C_r"],
                "by": { "center": "O", "angle": 90 }
            },
            {
                "type": "def_points_by_translation",
                "points_to_transform": ["A", "B", "C"],
                "new_ids": ["A_t", "B_t", "C_t"],
                "by": { "from_point": "V1", "to_point": "V2" }
            },

            // === PHASE 3: DESSIN DES FORMES TRANSFORMÉES ===
            { "type": "draw_polygon", "point_ids": ["A_r", "B_r", "C_r"], "style": {"color": "blue"} },
            { "type": "draw_polygon", "point_ids": ["A_t", "B_t", "C_t"], "style": {"color": "green", "fill_color": "green", "opacity": 0.1} },
            
            { "type": "label_points", "point_ids": ["A", "B", "C", "O", "A_r", "B_r", "C_r", "A_t", "B_t", "C_t"] }
        ]
    }
    ```