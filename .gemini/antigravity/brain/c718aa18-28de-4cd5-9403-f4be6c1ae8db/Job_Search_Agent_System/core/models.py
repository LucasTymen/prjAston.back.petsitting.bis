"""
Schémas Pydantic stricts pour l'ATV (Anti-Hallucination Vérifiable).
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ATVCheck(BaseModel):
    donnees_verifiees: bool = Field(description="Indique si les données ont été vérifiées par le système")
    hallucination_detectee: bool = Field(description="Indique si une hallucination a été détectée (non-conformité avec BASE_JSON)")
    commentaire: str = Field(description="Commentaire éventuel sur la validation")

class ScraperOutput(BaseModel):
    titre: str = Field(description="Titre de l'offre d'emploi")
    entreprise: str = Field(description="Nom de l'entreprise qui recrute")
    description_clean: str = Field(description="Description nettoyée de tout code HTML")
    mots_cles_detectes: List[str] = Field(description="Liste des mots-clés techniques ou métiers détectés")
    niveau_poste: str = Field(description="Niveau de séniorité requis")
    probleme_detecte: str = Field(description="Problème implicite que l'entreprise cherche à résoudre")

class MatchingOutput(BaseModel):
    persona_selectionne: str = Field(description="Le persona choisi parmi ceux disponibles dans BASE_JSON")
    secteur_detecte: str = Field(description="Le secteur d'activité de l'entreprise")
    exposition_seniorite: str = Field(description="La séniorité exposée pour matcher l'offre")
    score: int = Field(description="Score de compatibilité sur 100")
    next_action: str = Field(description="Action recommandée (POSTULER | PASSER | À surveiller)")
    arguments_actives: List[str] = Field(description="Liste des arguments du BASE_JSON retenus")
    mots_cles_ats: List[str] = Field(description="Liste des mots-clés de l'offre à injecter")

class FinalOutput(BaseModel):
    offre: Dict[str, Any]
    matching: Dict[str, Any]
    documents: Dict[str, str]
    canal_application: Dict[str, str]
    email_trouve: Dict[str, str]
    emails: Optional[Dict[str, str]] = None  # email_j0, email_j4, email_j10, sujet
    next_action: str
    date_relance_j4: str
    date_relance_j10: str
    ATV_CHECK: ATVCheck
