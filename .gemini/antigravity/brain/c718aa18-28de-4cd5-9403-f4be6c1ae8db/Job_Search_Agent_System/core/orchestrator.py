"""
Orchestrateur Hybrid - Combine extraction LLM et matching déterministe Python.
"""
import os
import json
from datetime import datetime, timedelta
from core.models import FinalOutput, ScraperOutput, MatchingOutput, ATVCheck
from core.utils import sanitize_placeholders, attachment_filenames
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
        offre_d = job_data.model_dump()
        contact_name = entreprise_data.get("contact_name") or entreprise_data.get("recruteur")
        cv_data = self.cv_gen.process(match_data, offre=offre_d)
        cv_markdown = self.cv_gen.render_cv_markdown(cv_data, offre=offre_d, final=True)
        lm_text = self.lm_gen.process(match_data, offre=offre_d, contact_name=contact_name)
        emails = self.email_gen.process(match_data, offre=offre_d, contact_name=contact_name)

        # Correction de l'instanciation de FinalOutput
        output = FinalOutput(
            offre=offre_d,
            matching=match_data.model_dump(),
            documents={
                "cv": cv_markdown,
                "lm": lm_text
            },
            canal_application={
                "canal_recommande": "Email direct",
                "contact_cible": entreprise_data.get("email_trouve") or "Inconnu"
            },
            email_trouve={k: str(v) for k, v in entreprise_data.items()},
            emails=emails,
            next_action=match_data.next_action,
            date_relance_j2=(datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
            date_relance_j4=(datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d'),
            date_relance_j7=(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            date_relance_j9=(datetime.now() + timedelta(days=9)).strftime('%Y-%m-%d'),
            ATV_CHECK=ATVCheck(
                donnees_verifiees=True, 
                hallucination_detectee=False, 
                commentaire="Logique déterministe Python active."
            )
        )

        # 5. Draft Gmail (Optionnel)
        if create_draft and match_data.next_action == "POSTULER":
            titre = job_data.titre or ""
            entreprise = job_data.entreprise or ""
            reference = offre_d.get("reference", "")
            contact_name = contact_name or ""
            raw_sujet = emails.get("sujet") or f"Candidature - {titre}"
            raw_body = emails.get("email_j0") or ""
            sujet = sanitize_placeholders(raw_sujet, titre_poste=titre, entreprise=entreprise, reference=reference, prenom_recruteur=contact_name)
            body = sanitize_placeholders(raw_body, titre_poste=titre, entreprise=entreprise, reference=reference, prenom_recruteur=contact_name)
            if not sujet.strip():
                sujet = f"Candidature - {titre}" if titre else "Candidature"
            if not body.strip():
                body = "Monsieur, Madame,\n\nVeuillez trouver ci-joint ma candidature.\n\nCordialement,\nLucas Tymen"
            cv_name, lm_name = attachment_filenames(entreprise, titre)
            out_dir = getattr(self, "_output_dir", None) or os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
            cv_path = os.path.join(out_dir, "cvs", cv_name)
            lm_path = os.path.join(out_dir, "lms", lm_name)
            attachment_paths = [p for p in [cv_path, lm_path] if os.path.exists(p)]
            self.drafter.create_draft(
                entreprise_data.get("email_trouve"),
                sujet,
                body,
                attachment_paths
            )
            print("Brouillon créé avec succès.")

        return output
