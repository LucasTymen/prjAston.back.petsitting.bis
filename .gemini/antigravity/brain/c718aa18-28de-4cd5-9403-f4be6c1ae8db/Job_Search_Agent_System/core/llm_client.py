"""
Client unifié pour les appels LLM (Groq, OpenAI, Ollama).
"""
import os
import json
from groq import Groq
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIClient:
    """
    Client centralisé supportant plusieurs providers (Groq par défaut, OpenAI/Ollama en fallback).
    Note: Garde le nom OpenAIClient pour rétro-compatibilité temporaire avec les agents existants.
    """
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        
        # Choix du provider (Groq prioritaire si clé présente)
        if self.groq_key:
            self.provider = "groq"
            self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
            self.client = Groq(api_key=self.groq_key)
        elif self.openai_key:
            self.provider = "openai"
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            self.client = OpenAI(api_key=self.openai_key)
        else:
            self.provider = "ollama"
            self.model = os.getenv("OLLAMA_MODEL", "llama3")
            self.client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

    def chat_completion(self, prompt: str, system_prompt: str = "Tu es un assistant expert en recrutement et automatisation.", json_mode: bool = True) -> dict:
        """
        Effectue un appel de complétion chat sur le provider actif.
        """
        response_format = {"type": "json_object"} if json_mode else None
        
        # Ajustement format pour Groq si json_mode (Groq supporte json_object sur certains modèles)
        # Mais pour plus de sécurité on peut aussi forcer dans le prompt si besoin.
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format=response_format if self.provider in ["openai", "groq"] else None,
                timeout=60,
            )
            content = response.choices[0].message.content
            if json_mode:
                # Nettoyage minimal pour Ollama ou modèles ne respectant pas strictement le JSON format
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                return json.loads(content)
            return {"content": content}
        except Exception as e:
            print(f"Erreur LLM ({self.provider}): {e}")
            return {}

    def get_embedding(self, text: str, model: str = "text-embedding-3-small") -> list:
        """
        Génère un embedding (fallback OpenAI uniquement car Groq ne fait pas d'embeddings nativement standard).
        """
        if not self.openai_key:
            print("Erreur: OPENAI_API_KEY requis pour les embeddings.")
            return []
            
        try:
            client_oa = OpenAI(api_key=self.openai_key)
            text = text.replace("\n", " ")
            return client_oa.embeddings.create(input=[text], model=model).data[0].embedding
        except Exception as e:
            print(f"Erreur OpenAI Embedding: {e}")
            return []
