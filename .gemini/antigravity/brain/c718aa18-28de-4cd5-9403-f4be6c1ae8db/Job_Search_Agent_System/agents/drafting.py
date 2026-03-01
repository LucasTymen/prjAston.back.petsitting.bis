"""
Agent de mise en brouillon sur Gmail via IMAP avec pièces jointes.
"""
import imaplib
import time
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

load_dotenv()

class GmailDraftingAgent:
    def __init__(self):
        self.user = os.getenv("GMAIL_USER")
        self.password = os.getenv("GMAIL_APP_PASSWORD")
        self.host = "imap.gmail.com"

    def create_draft(self, to_email: str, subject: str, body: str, attachment_paths: list = None) -> bool:
        """
        Crée un brouillon avec des pièces jointes optionnelles.
        """
        if not self.user or not self.password:
            print("Erreur: GMAIL_USER ou GMAIL_APP_PASSWORD non configuré dans .env")
            return False

        try:
            # Création du message multi-part
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = self.user
            msg['To'] = to_email
            
            # Corps de l'email
            msg.attach(MIMEText(body, 'plain'))

            # Pièces jointes
            if attachment_paths:
                for path in attachment_paths:
                    if os.path.exists(path):
                        with open(path, "rb") as f:
                            part = MIMEApplication(f.read(), Name=os.path.basename(path))
                            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(path)}"'
                            msg.attach(part)
                    else:
                        print(f"Attention: Le fichier {path} n'existe pas.")

            # Connexion IMAP
            mail = imaplib.IMAP4_SSL(self.host)
            mail.login(self.user, self.password)

            # Recherche du dossier Brouillons
            draft_folder = None
            typ, folders = mail.list()
            if typ == 'OK':
                for f in folders:
                    fd = f.decode()
                    if r'\Drafts' in fd:
                        parts = fd.split(' "/" ')
                        if len(parts) > 1:
                            draft_folder = parts[1].strip('"')
                            break

            if not draft_folder:
                draft_folder = "[Gmail]/Drafts"

            mail.append(draft_folder, '', imaplib.Time2Internaldate(time.time()), msg.as_bytes())
            mail.logout()
            return True

        except Exception as e:
            print(f"Erreur lors de la création du brouillon avec attachment: {e}")
            return False
