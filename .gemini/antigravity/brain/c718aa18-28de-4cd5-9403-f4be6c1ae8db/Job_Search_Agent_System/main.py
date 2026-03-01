import json
from core.orchestrator import Orchestrator

def main():
    print("Démarrage du système...")
    # Charger manuellement le base_json ici
    try:
        with open("resources/base.json", "r", encoding="utf-8") as f:
            base_json = json.load(f)
    except FileNotFoundError:
        print("Erreur: Le fichier resources/base.json est introuvable.")
        print("Veuillez déposer votre profil JSON de référence dans le dossier 'resources' sous le nom 'base.json'.")
        return

    orchestrator = Orchestrator(base_json=base_json)
    # Remplacer par l'URL cible
    orchestrator.run_pipeline("https://www.welcometothejungle.com/fr/jobs/exemple")

if __name__ == "__main__":
    main()
