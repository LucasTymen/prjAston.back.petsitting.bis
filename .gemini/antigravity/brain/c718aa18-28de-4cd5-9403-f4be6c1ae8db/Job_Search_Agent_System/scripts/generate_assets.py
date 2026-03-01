import os
import sys

# Ajout du chemin racine pour l'import des agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.cv_pdf import CvPdfGenerator
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class FullCampaignAssetGenerator:
    def __init__(self, output_dir="outputs"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.cv_gen = CvPdfGenerator(output_dir=os.path.join(output_dir, "cvs"))
        
    def generate_lm_pdf(self, filename, lm_text):
        filepath = os.path.join(self.output_dir, "lms", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter, leftMargin=72, rightMargin=72, topMargin=72, bottomMargin=72)
        styles = getSampleStyleSheet()
        normal_style = styles['Normal']
        normal_style.fontSize = 11
        normal_style.leading = 14
        
        story = []
        
        # Split text by double newlines for paragraphs
        for part in lm_text.split("\n\n"):
            story.append(Paragraph(part.replace("\n", "<br/>"), normal_style))
            story.append(Spacer(1, 12))
            
        doc.build(story)
        return filepath

def main():
    # DONNÉES RÉELLES SANS PLACEHOLDERS
    cv_data = {
        "nom": "LUCAS TYMEN",
        "adresse": "Maisons-Alfort (94700).",
        "telephone": "06 62 09 82 57",
        "email": "lucas.tymen@gmail.com",
        "linkedin": "https://www.linkedin.com/in/lucas-tymen-310255123/",
        "titre_poste": "CONSULTANT DIGITAL & GROWTH OPERATIONS",
        "profil": "Expert en <b>transformation digitale</b>, <b>automatisation</b> et <b>stratégie data</b>, avec 20+ ans d’expérience en <b>IT</b> et <b>gestion de projets artistiques/commerciaux</b>. Double compétence : <b>technique</b> (Python, n8N, ATS) et <b>artistique</b> (vente de matériel, conseil aux professionnels).",
        "competences_ats": {
            "IT/Dev": ["Python", "n8n", "Flowise", "Comet", "ATS", "automatisation", "Django", "Java", "GLPI", "Active Directory"],
            "Growth/SEO": ["Google Ads", "Meta Ads", "SEO technique", "GA4", "GTM", "Looker Studio", "scraping B2B"],
            "Art/Commerce": ["Vente B2B/B2C (matériel artistique)", "gestion de rayon (800–1500 références)", "logistique fournisseurs", "conseil aux architectes/artistes"]
        },
        "experiences": [
            {
                "entite": "Parazar",
                "role": "Growth Ops & Automation Lead",
                "periode": "2025",
                "bullets": [
                    "Automatisation d’un algorithme de matching → Gain : 2h par session (~87€ économisés).",
                    "Mise en place d’un reporting automatisé (n8n + IA) → +70% gain de temps."
                ]
            },
            {
                "entite": "A.P.S.I.",
                "role": "Responsable IT & Systèmes",
                "periode": "2000–2022",
                "bullets": [
                    "Gestion parc multisite (~300 postes) et implémentation GLPI.",
                    "Administration réseaux & Active Directory."
                ]
            }
        ],
        "formation": [
            {"ecole": "Rocket School", "diplome": "Growth & Performance", "annee": "2025"},
            {"ecole": "Le Wagon", "diplome": "Développement Web", "annee": "2022"},
            {"ecole": "Aston", "diplome": "POEC Java / Angular", "annee": "2023"}
        ],
        "projet_pro": "Recherche une mission opérationnelle en <b>marketing digital</b> ou <b>acquisition</b>, avec intervention sur des problématiques de <b>performance mesurable</b>. Disponible immédiatement en <b>Île-de-France</b>."
    }

    lm_text = """LUCAS TYMEN
Maisons-Alfort (94700).
06 62 09 82 57
lucas.tymen@gmail.com
https://www.linkedin.com/in/lucas-tymen-310255123/

28 février 2026

Responsable Recrutement
Orange Travel
111 Quai du Président Roosevelt
92130 ISSY-LES-MOULINEAUX

Objet : Candidature – Responsable SEO (F/H)

Madame, Monsieur,

Votre offre pour le poste de Responsable SEO chez Orange Travel m’a immédiatement interpellé. Mon profil hybride alliant SEO technique, automatisation data-driven, et gestion de projets digitaux correspond parfaitement aux enjeux d'internalisation de vos compétences SEO.

SEO Technique & Audit : Chez Parazar, j’ai optimisé la délivrabilité email (de 4.6 à 10/10) et généré 908 leads qualifiés via des automatisations complexes. Avec SquidResearch, j’ai conçu un SaaS Django scalable capable d'orchestrer 1388 requêtes/s, prouvant ma capacité à gérer des infrastructures techniques exigeantes pour le SEO.

Stratégie Éditoriale & Automatisation : Ma maîtrise de n8n et Claude AI me permet d'automatiser non seulement la technique, mais aussi les flux éditoriaux et l'acquisition. À titre d'exemple, j'ai réduit de 2h le temps de traitement manuel par session chez Parazar grâce à des pipelines data intelligents.

Engagement et Résultats : Je ne propose pas seulement du conseil, mais une exécution directe et chiffrée. Mon approche combine l'expertise technique des outils (Screaming Frog, GA4, GTM) avec une vision business claire : augmenter la performance mesurable de vos campagnes SEO.

Je serais ravi d’échanger sur la manière dont mon expertise pourra renforcer la visibilité organique d’Orange Travel, notamment sur le déploiement de vos solutions eSIM.

Cordialement,

LUCAS TYMEN"""

    gen = FullCampaignAssetGenerator()
    cv_path = gen.cv_gen.generate("CV_Lucas_Tymen_Orange_Travel.pdf", cv_data)
    lm_path = gen.generate_lm_pdf("LM_Lucas_Tymen_Orange_Travel.pdf", lm_text)
    
    print(f"CV généré : {cv_path}")
    print(f"LM générée : {lm_path}")

if __name__ == "__main__":
    main()
