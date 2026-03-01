"""
MatchingEngine Deterministe - Scoring Python pur basé sur les règles du JSON.
"""
import json
from typing import List, Dict
from core.models import MatchingOutput, ScraperOutput

class MatchingEngine:
    def __init__(self, base_json: dict):
        self.base_json = base_json
        self.personas = self.base_json.get("personas_specialises", {})
        self.persona_engine = self.base_json.get("persona_engine", {})

    def process(self, scraper_data: ScraperOutput) -> MatchingOutput:
        """
        Logique déterministe en Python pour le matching et le scoring.
        """
        # 1. Scoring des personas par intersection de mots-clés
        scores = self._score_all_personas(scraper_data.mots_cles_detectes)
        
        if not scores:
            print("Aucun match trouvé, utilisation du fallback.")
            best_persona_name = "it_support_pme"
            final_score = 0
        else:
            best_persona_name = max(scores, key=lambda k: scores[k]["score"])
            final_score = int(scores[best_persona_name]["score"])
            
        best_persona_data = self.personas.get(best_persona_name, {})
        
        # 2. Détermination de la séniorité exposée
        # Si Strategique ou Senior détecté par Scraper -> Strategique
        exposition = "Strategique" if scraper_data.niveau_poste.lower() in ["senior", "strategique"] else "Operationnelle"
        
        # 3. Détermination de l'action suivante
        next_action = "PASSER"
        if final_score >= 60: next_action = "POSTULER"
        elif final_score >= 30: next_action = "À surveiller"

        return MatchingOutput(
            persona_selectionne=best_persona_name,
            secteur_detecte=self._detect_secteur(best_persona_name),
            exposition_seniorite=exposition,
            score=final_score,
            next_action=next_action,
            arguments_actives=best_persona_data.get("arguments_prioritaires", []),
            mots_cles_ats=scraper_data.mots_cles_detectes[:10]
        )

    def _score_all_personas(self, keywords_offre: List[str]) -> Dict[str, dict]:
        results = {}
        # Poids par type (si défini dans le moteur du JSON)
        poids_config = self.persona_engine if isinstance(self.persona_engine, dict) else {}
        poids_tech = poids_config.get("poids_par_type", {}).get("competence_technique", 3)
        
        if not self.personas:
             return {}

        for name, data in self.personas.items():
            # Comparaison insensible à la casse
            keywords_persona = [k.lower() for k in data.get("mots_cles_detection", [])]
            keywords_job = [k.lower() for k in keywords_offre]
            
            intersection = set(keywords_job) & set(keywords_persona)
            
            # Score de base: 3 points par mot-clé matché
            score_brut = len(intersection) * poids_tech
            
            # Bonus si le nom du persona est dans le titre de l'offre
            # results[name] = {"score": min(score_brut * 10, 100), "matches": list(intersection)}
            
            # On stocke le score
            # Pour SEO technique (Orange) : keywords extraits [SEO technique, IA, GA4...]
            # Keywords persona [SEO, technique, GA4, GTM...] -> Match tech
            results[name] = {"score": min(score_brut * 15, 100), "matches": list(intersection)}
            
        return results

    def _detect_secteur(self, persona_name: str) -> str:
        if "it_support" in persona_name: return "it_support"
        if "vente" in persona_name: return "vente"
        return "growth_seo_data_dev"
