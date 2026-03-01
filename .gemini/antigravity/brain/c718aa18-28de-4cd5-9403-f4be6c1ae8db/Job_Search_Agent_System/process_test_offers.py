import json
import os
import sys

# Ajout du path pour import core/agents si besoin
sys.path.append(os.getcwd())

from core.orchestrator import Orchestrator

# Les offres fournies par l'utilisateur
OFFRES = [
    {
        "url": "https://www.hellowork.com/fr-fr/emplois/24032203.html",
        "titre": "Commercial en Galerie d'Art (CDI)",
        "entreprise": "Capital Ressources"
    },
    {
        "url": "https://fr.jooble.org/emploi-vendeur-beaux-arts/Paris-(75)",
        "titre": "Vendeur(se) Beaux-Arts (CDI)",
        "entreprise": "Fondation Cartier"
    },
    {
        "url": "https://fr.indeed.com/q-galerie-d-art-l-paris-(75)-emplois.html",
        "titre": "Conseiller de Vente en Galerie d'Art (H/F)",
        "entreprise": "Carré d'Artistes"
    }
]

def main():
    print("Démarrage du test pour les 3 offres Art/Vente...")
    
    # Charger le profil complet (celui avec l'expérience vente)
    base_json_path = "resources/cv_base_datas_pour_candidatures.json"
    
    if not os.path.exists(base_json_path):
        print(f"Erreur: {base_json_path} introuvable.")
        return

    try:
        with open(base_json_path, "r", encoding="utf-8") as f:
            base_json = json.load(f)
    except Exception as e:
        print(f"Erreur: Impossible de charger {base_json_path}: {e}")
        return

    orchestrator = Orchestrator(base_json=base_json)

    for i, offre in enumerate(OFFRES, 1):
        print(f"\n--- Traitement Offre {i}: {offre['titre']} @ {offre['entreprise']} ---")
        try:
            # On active create_draft=True
            output = orchestrator.run_pipeline(offre['url'], create_draft=True)
            print(f"Action suivante: {output.next_action}")
        except Exception as e:
            print(f"Erreur lors du traitement de l'offre {i}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
