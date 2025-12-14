import logging

# 1. On importe le Singleton Registry (l'entrepôt)
from src.core.registry import tool_registry

# 2. On importe les Outils Concrets (les ouvriers)
# C'est ici que tu ajouteras tes futurs imports (ChemistryTool, GraphTool, etc.)
from src.features.tools.geometry_2d.tool import Geometry2DTool

log = logging.getLogger(__name__)

def register_application_tools():
    """
    Fonction exécutée au démarrage de l'API.
    Son rôle est d'instancier chaque outil et de l'enregistrer dans le registre central.
    """
    log.info("🛠️  Initialisation des outils Neuclid...")

    # --- ENREGISTREMENT DES OUTILS ---
    
    # 1. Outil Géométrie 2D
    try:
        # On instancie l'outil (ce qui charge ses prompts et sa config)
        geo_tool = Geometry2DTool()
        # On l'ajoute au registre
        tool_registry.register(geo_tool)
    except Exception as e:
        log.error(f"❌ Échec de l'enregistrement de Geometry2DTool : {e}", exc_info=True)

    # 2. Emplacement pour les futurs outils (Variation, Graphes, etc.)
    # try:
    #     variation_tool = VariationTableTool()
    #     tool_registry.register(variation_tool)
    # except...

    # --- FIN ENREGISTREMENT ---

    count = len(tool_registry.get_all_tools())
    log.info(f"✅ Registre d'outils prêt : {count} outil(s) chargé(s) et disponibles pour le Routeur.")