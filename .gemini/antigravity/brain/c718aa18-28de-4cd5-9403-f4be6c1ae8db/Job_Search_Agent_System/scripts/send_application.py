import os
import sys

# Ajout du chemin racine pour l'import des agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.drafting import GmailDraftingAgent
from core.utils import attachment_filenames

# Charte nommage : CV_Lucas_Tymen_{société}_{intitulé}.pdf
ENTREPRISE = "Orange Travel"
TITRE_POSTE = "Responsable SEO (F/H)"

def main():
    agent = GmailDraftingAgent()
    cv_name, lm_name = attachment_filenames(ENTREPRISE, TITRE_POSTE)

    to_email = 'contact@travel-orange.com'
    subject = f'Candidature – {TITRE_POSTE} – Lucas Tymen'
    
    # Corps avec DONNÉES RÉELLES (Tél, LinkedIn)
    body = '''Bonjour,

Je me permets de vous adresser ma candidature pour le poste de Responsable SEO au sein d’Orange Travel.

Vous trouverez ci-joint :
- Mon CV (Format ATS), détaillant mon expertise en SEO technique, automatisation data-driven (908 leads générés), et gestion de projets digitaux.
- Ma lettre de motivation, expliquant comment mes réalisations (ex : délivrabilité email 10/10) pourraient contribuer à vos objectifs.
- Un lien vers une landing démonstrative [https://lppp-infopro.vercel.app/], illustrant mon approche combinant audit SEO et automatisation.

Je reste à votre disposition pour un échange téléphonique au 06 62 09 82 57 ou une rencontre.

Cordialement,

LUCAS TYMEN
06 62 09 82 57
https://www.linkedin.com/in/lucas-tymen-310255123/'''

    cv_path = os.path.join('outputs', 'cvs', cv_name)
    lm_path = os.path.join('outputs', 'lms', lm_name)
    
    attachments = []
    if os.path.exists(cv_path):
        attachments.append(cv_path)
    if os.path.exists(lm_path):
        attachments.append(lm_path)
        
    print(f'Tentative de création de brouillon pour {to_email} avec {len(attachments)} pièces jointes...')
    
    success = agent.create_draft(to_email, subject, body, attachment_paths=attachments)
        
    if success:
        print('Brouillon créé avec succès dans Gmail !')
    else:
        print('Erreur lors de la création du brouillon.')

if __name__ == '__main__':
    main()
