"""
Test de validation pour Groq.
"""
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def test_groq():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        print("GROQ_API_KEY non trouvée dans le .env")
        return

    print(f"Test de la clé Groq (commençant par {key[:7]}...)")
    try:
        client = Groq(api_key=key)
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Réponds juste : OK"}]
        )
        print(f"Réponse Groq : {r.choices[0].message.content}")
    except Exception as e:
        print(f"Erreur Groq : {e}")

if __name__ == '__main__':
    test_groq()
