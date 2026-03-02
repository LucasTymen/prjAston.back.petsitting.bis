from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

class CvPdfGenerator:
    """
    Générateur de PDF pour les CV (Format ATS Clean) et Lettres de Motivation.
    """
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        self.cv_dir = os.path.join(output_dir, "cvs")
        self.lm_dir = os.path.join(output_dir, "lms")
        for d in [self.cv_dir, self.lm_dir]:
            if not os.path.exists(d):
                os.makedirs(d)

    def generate(self, filename: str, cv_data: dict) -> str:
        """
        Génère un fichier PDF à partir des données du CV (Format ATS Clean).
        """
        filepath = os.path.join(self.cv_dir, filename)
        
        try:
            doc = SimpleDocTemplate(filepath, pagesize=letter, leftMargin=72, rightMargin=72, topMargin=72, bottomMargin=72)
            styles = getSampleStyleSheet()
            
            normal_style = styles['Normal']
            normal_style.fontSize = 11
            normal_style.leading = 14
            
            bold_style = styles['Heading3']
            bold_style.fontSize = 12
            bold_style.spaceAfter = 6
            bold_style.spaceBefore = 12
            
            title_style = styles['Title']
            title_style.fontSize = 14
            title_style.alignment = 0 # Gauche
            title_style.spaceAfter = 2
            
            story = []

            # 1. CARTOUCHE
            story.append(Paragraph(f"<b>{cv_data.get('nom', 'LUCAS TYMEN').upper()}</b>", title_style))
            story.append(Paragraph(cv_data.get('adresse', ''), normal_style))
            story.append(Paragraph(cv_data.get('telephone', ''), normal_style))
            story.append(Paragraph(cv_data.get('email', ''), normal_style))
            story.append(Paragraph(cv_data.get('linkedin', ''), normal_style))
            story.append(Spacer(1, 12))

            # 2. TITRE DE POSTE
            story.append(Paragraph(f"<b>{cv_data.get('titre_poste', '').upper()}</b>", bold_style))
            story.append(Spacer(1, 12))

            # 3. PROFIL
            story.append(Paragraph("<b>Profil</b>", bold_style))
            story.append(Paragraph(cv_data.get('profil', ''), normal_style))

            # 4. COMPÉTENCES
            story.append(Paragraph("<b>Compétences</b>", bold_style))
            for cat, comps in cv_data.get('competences_ats', {}).items():
                story.append(Paragraph(f"<b>{cat}</b> : {', '.join(comps)}", normal_style))

            # 5. EXPÉRIENCES
            story.append(Paragraph("<b>Expériences</b>", bold_style))
            for exp in cv_data.get('experiences', []):
                header = f"<b>{exp.get('role')} – {exp.get('entite')} ({exp.get('periode')})</b>"
                story.append(Paragraph(header, normal_style))
                for bullet in exp.get('bullets', []):
                    story.append(Paragraph(bullet, normal_style))
                story.append(Spacer(1, 6))

            # 6. FORMATION (compatible generator: etablissement/intitule/annee ou ecole/diplome/annee)
            story.append(Paragraph("<b>Formation</b>", bold_style))
            for edu in cv_data.get('formation', []):
                ecole = edu.get('ecole') or edu.get('etablissement', '')
                diplome = edu.get('diplome') or edu.get('intitule') or edu.get('niveau', '')
                annee = edu.get('annee', '')
                story.append(Paragraph(f"<b>{ecole}</b> – {diplome} ({annee})", normal_style))

            doc.build(story)
            return filepath
        except Exception as e:
            print(f"Erreur lors de la génération du CV PDF : {e}")
            return None

    def generate_lm(self, filename: str, lm_text: str) -> str:
        """
        Génère un fichier PDF pour la lettre de motivation.
        """
        filepath = os.path.join(self.lm_dir, filename)
        try:
            doc = SimpleDocTemplate(filepath, pagesize=letter, leftMargin=72, rightMargin=72, topMargin=72, bottomMargin=72)
            styles = getSampleStyleSheet()
            normal_style = styles['Normal']
            normal_style.fontSize = 11
            normal_style.leading = 14
            
            story = []
            for part in lm_text.split("\n\n"):
                story.append(Paragraph(part.replace("\n", "<br/>"), normal_style))
                story.append(Spacer(1, 12))
                
            doc.build(story)
            return filepath
        except Exception as e:
            print(f"Erreur lors de la génération de la LM PDF : {e}")
            return None
