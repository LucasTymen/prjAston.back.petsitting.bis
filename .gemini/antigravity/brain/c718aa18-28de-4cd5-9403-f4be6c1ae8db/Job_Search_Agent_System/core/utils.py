"""
Utilitaires partagés : sanitisation des placeholders, nommage des pièces jointes.
"""
import re


def sanitize_placeholders(
    text: str,
    *,
    titre_poste: str = "",
    entreprise: str = "",
    reference: str = "",
    prenom_recruteur: str = "",
) -> str:
    """
    Remplace les placeholders {{...}} par les valeurs fournies.
    Si une donnée manque, on met une chaîne vide (pas de placeholder laissé).
    Tout autre {{xxx}} restant est supprimé (remplacé par vide).
    """
    if not text or not isinstance(text, str):
        return text
    # Remplacements explicites
    text = text.replace("{{titre_poste}}", titre_poste or "")
    text = text.replace("{{Titre_poste}}", titre_poste or "")
    text = text.replace("{{prenom_recruteur}}", prenom_recruteur or "")
    text = text.replace("{{Prenom_recruteur}}", prenom_recruteur or "")
    text = text.replace("{{entreprise}}", entreprise or "")
    text = text.replace("{{reference}}", reference or "")
    # Tout autre {{...}} → vide (ne jamais laisser de placeholder)
    text = re.sub(r"\s*\{\{[^}]*\}\}\s*", " ", text)
    # Nettoyer les espaces multiples (préserver les retours à la ligne)
    text = re.sub(r"[ \t]+", " ", text).strip()
    return text


def attachment_filenames(entreprise: str, titre_poste: str, base_name: str = "Lucas_Tymen") -> tuple[str, str]:
    """
    Retourne les noms de fichiers des pièces jointes selon la charte :
    CV_{base}_société_intitulé.pdf, LM_{base}_société_intitulé.pdf
    Ex. CV_Lucas_Tymen_orange_SOE_technique.pdf
    """
    def _slug(s: str) -> str:
        if not s:
            return ""
        s = s.strip().replace(" ", "_").replace("/", "-").replace("(", "").replace(")", "")
        s = re.sub(r"[^\w\-.]", "", s)
        return s[:80] or "poste"

    soc = _slug(entreprise or "entreprise")
    tit = _slug(titre_poste or "poste")
    suffix = f"{soc}_{tit}" if soc and tit else (soc or tit)
    cv_name = f"CV_{base_name}_{suffix}.pdf"
    lm_name = f"LM_{base_name}_{suffix}.pdf"
    return cv_name, lm_name
