"""
Validateur ATV (Anti-Hallucination Vérifiable)
"""
import re
import json
from typing import Union

def extract_numbers(texte: str) -> list[str]:
    """Extrait tous les nombres d'une chaîne de caractères."""
    return re.findall(r'\b\d+\b', texte)

def _get_all_strings_from_dict(d: Union[dict, list, str, int, float]) -> str:
    """Récupère récursivement toutes les valeurs textuelles/numériques d'un JSON."""
    if isinstance(d, dict):
        return " ".join([_get_all_strings_from_dict(v) for v in d.values()])
    elif isinstance(d, list):
        return " ".join([_get_all_strings_from_dict(v) for v in d])
    elif isinstance(d, (str, int, float)):
        return str(d)
    return ""

def extract_roles(base_json: dict) -> list[str]:
    """Extrait les rôles depuis le base_json."""
    roles = []
    if "reference_canonique_periodes_roles" in base_json:
        for ex in base_json["reference_canonique_periodes_roles"]:
            if "role" in ex:
                roles.append(ex["role"])
    return roles

def extract_dates(base_json: dict) -> list[str]:
    """Extrait les dates de début et de fin."""
    dates = []
    if "reference_canonique_periodes_roles" in base_json:
        for ex in base_json["reference_canonique_periodes_roles"]:
            if "debut" in ex:
                dates.append(ex["debut"])
            if "fin" in ex:
                dates.append(ex["fin"])
    return dates

def valider_donnees(base_json: dict, data_to_check: Union[dict, str]) -> tuple[bool, str]:
    """
    Vérifie que les données générées ne contiennent aucune hallucination (chiffre inventé).
    """
    text_to_check = data_to_check if isinstance(data_to_check, str) else _get_all_strings_from_dict(data_to_check)
    
    # 1. Extraire tous les nombres du texte généré
    nombres_generes = set(extract_numbers(text_to_check))
    
    if not nombres_generes:
        return True, "Validation OK"

    # 2. Extraire tous les nombres autorisés depuis le base_json (vérité absolue)
    base_text = _get_all_strings_from_dict(base_json)
    nombres_autorises = set(extract_numbers(base_text))
    
    # 3. Vérifier chaque chiffre généré
    for num in nombres_generes:
        if num not in nombres_autorises:
            return False, f"Hallucination détectée : le chiffre '{num}' n'existe pas dans le profil de base."
            
    #TODO: Ajouter la validation stricte des intitulés de rôles si nécessaire.
    return True, "Validation OK"
