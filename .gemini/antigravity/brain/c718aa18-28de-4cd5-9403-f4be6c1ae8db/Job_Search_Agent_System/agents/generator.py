"""
Agents de génération (CV, LM, Email) raffinés avec protection PII stricte.
"""
import json
from core.models import MatchingOutput
from core.llm_client import OpenAIClient

ANTI_AI_PROMPT = """
Tu es un correcteur éditorial expert dans la détection et la neutralisation des marqueurs de texte générés par intelligence artificielle.
Ton rôle est d'adopter un ton humain, nuancé, fluide, sans structure artificielle, ni marqueurs typiques de génération LLM.
"""

def _minify_json_safe(data: dict, remove_pii: bool = True) -> str:
    """
    Purge TOUT ce qui est identifiable : meta, narratifs persos, arguments personnalisés.
    Ne garde que les 'briques' techniques et professionnelles neutres.
    """
    minified = {
        "experiences": [],
        "arguments_competences": []
    }
    
    for exp in data.get("experiences", []):
        minified["experiences"].append({
            "entite": exp.get("entite"),
            "role": exp.get("role") or exp.get("role_it"),
            "periode": exp.get("periode"),
            "points_cles": exp.get("bullet_cv_court")
        })
        
    for group, args in data.get("arguments_reutilisables", {}).items():
        if isinstance(args, list):
            for item in args:
                if isinstance(item, dict) and "argument" in item:
                    minified["arguments_competences"].append(item.get("argument"))
            
    return json.dumps(minified, ensure_ascii=False)

class CvAtvGenerator:
    """
    Générateur de structure de CV (Logique locale déterministe).
    """
    def __init__(self, base_json: dict):
        self.base_json = base_json
        
    def process(self, matching_data: MatchingOutput) -> dict:
        meta = self.base_json.get("meta", {})
        cv_data = {
            "nom": meta.get("nom", "Lucas Tymen"),
            "adresse": meta.get("adresse", ""),
            "telephone": meta.get("telephone", ""),
            "email": meta.get("email", ""),
            "linkedin": meta.get("linkedin", ""),
            "titre_poste": matching_data.persona_selectionne,
            "profil": self.base_json.get("narratifs_candidature", {}).get(self._get_narratif_key(matching_data), ""),
            "experiences": [],
            "competences_ats": {"Compétences": matching_data.mots_cles_ats},
            "formation": []
        }
        # On remplit les expériences pour le PDF final
        for exp in self.base_json.get("experiences", []):
             cv_data["experiences"].append({
                 "entite": exp.get("entite"),
                 "role": exp.get("role") or exp.get("role_it"),
                 "periode": exp.get("periode"),
                 "bullets": exp.get("bullet_cv_court", [])
             })
        return cv_data

    def _get_narratif_key(self, matching_data):
        secteur = matching_data.secteur_detecte
        if secteur == "it_support": return "it_support_pme"
        if "growth" in secteur or "seo" in secteur: return "accroche_growth"
        if secteur == "vente": return "accroche_vente"
        return "it_support_pme"

class LmCoordinator:
    def __init__(self, base_json: dict):
        self.base_json = base_json
        self.llm = OpenAIClient()
        
    def process(self, matching_data: MatchingOutput) -> str:
        meta = self.base_json.get("meta", {})
        coordonnees = f"{meta.get('nom')}\n{meta.get('adresse')}\n{meta.get('telephone')}\n{meta.get('email')}\n{meta.get('linkedin')}"
        min_json_safe = _minify_json_safe(self.base_json)
        
        prompt = f"""
{ANTI_AI_PROMPT}

MISSION :
Rédiger une lettre de motivation pour le poste de {matching_data.persona_selectionne} chez Orange Travel.
Utilise les points clés suivants (SANS les inventer) :
{min_json_safe}

L'offre d'emploi porte sur : {matching_data.mots_cles_ats}

CONSIGNES :
- Ton pro, humain, sans listes à puces.
- Signature : Lucas Tymen.
"""
        res = self.llm.chat_completion(prompt, system_prompt="Écrivain pro.", json_mode=False)
        return res.get("content", "Erreur.")

class EmailEngine:
    def __init__(self, base_json: dict):
        self.base_json = base_json
        self.llm = OpenAIClient()
        
    def process(self, matching_data: MatchingOutput) -> dict:
        min_json_safe = _minify_json_safe(self.base_json)
        prompt = f"""
{ANTI_AI_PROMPT}
MISSION : Générer les emails J0, J4, J10 pour le poste {matching_data.persona_selectionne}.
Briques pro : {min_json_safe}

OUTPUT JSON: {{ "email_j0": "...", "email_j4": "...", "email_j10": "...", "sujet": "..." }}
"""
        return self.llm.chat_completion(prompt, json_mode=True)
