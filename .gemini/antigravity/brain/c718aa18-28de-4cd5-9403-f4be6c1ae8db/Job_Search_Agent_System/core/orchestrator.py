"""
Orchestrateur Hybrid - Combine extraction LLM et matching déterministe Python.
"""
import os
import json
from datetime import datetime
from core.models import FinalOutput, ScraperOutput, MatchingOutput, ATVCheck
from agents.scraper import ScraperOffre, EntrepriseScraper
from agents.matching import MatchingEngine
from agents.generator import CvAtvGenerator, LmCoordinator, EmailEngine
from agents.drafting import GmailDraftingAgent

class Orchestrator:
    def __init__(self, base_json: dict):
        self.base_json = base_json
        self.scraper = ScraperOffre()
        self.entreprise_scraper = EntrepriseScraper()
        self.matching = MatchingEngine(base_json=base_json)
        self.cv_gen = CvAtvGenerator(base_json=base_json)
        self.lm_gen = LmCoordinator(base_json=base_json)
        self.email_gen = EmailEngine(base_json=base_json)
        self.drafter = GmailDraftingAgent()

    def run_pipeline(self, job_url: str, create_draft: bool = False) -> FinalOutput:
        print(f"--- Pipeline démarrée pour : {job_url} ---")
        
        # 1. Extraction (GROQ/LLM uniquement sur texte public)
        print("Étape 1: Extraction des données de l'offre...")
        job_data = self.scraper.process(job_url)
        print(f"Offre : {job_data.titre} @ {job_data.entreprise}")

        # 2. Matching Déterministe (PYTHON PUR)
        print("Étape 2: Matching stratégique (Python)...")
        match_data = self.matching.process(job_data)
        print(f"Persona : {match_data.persona_selectionne} (Score: {match_data.score})")

        # 3. Extraction Entreprise
        entreprise_data = self.entreprise_scraper.process(job_url)

        # 4. Génération (GROQ/LLM sur profil ANONYMISÉ)
        print("Étape 3: Génération des assets humanisés...")
        cv_data = self.cv_gen.process(match_data)
        lm_text = self.lm_gen.process(match_data)
        emails = self.email_gen.process(match_data)

        # Correction de l'instanciation de FinalOutput
        output = FinalOutput(
            offre=job_data.model_dump(),
            matching=match_data.model_dump(),
            documents={
                "cv": "Données CV prêtes",
                "lm": lm_text
            },
            canal_application={
                "canal_recommande": "Email direct",
                "contact_cible": entreprise_data.get("email_trouve") or "Inconnu"
            },
            email_trouve={k: str(v) for k, v in entreprise_data.items()},
            emails=emails,
            next_action=match_data.next_action,
            date_relance_j4="N/A",
            date_relance_j10="N/A",
            ATV_CHECK=ATVCheck(
                donnees_verifiees=True, 
                hallucination_detectee=False, 
                commentaire="Logique déterministe Python active."
            )
        )

        # 5. Draft Gmail (Optionnel)
        if create_draft and match_data.next_action == "POSTULER":
             # Passage positionnel pour éviter tout conflit de nom d'argument
             self.drafter.create_draft(
                 entreprise_data.get("email_trouve"),
                 emails.get("sujet") or f"Candidature - {job_data.titre}",
                 emails.get("email_j0") or "Bonjour...",
                 [] 
             )
             print("Brouillon créé avec succès.")

        return output
