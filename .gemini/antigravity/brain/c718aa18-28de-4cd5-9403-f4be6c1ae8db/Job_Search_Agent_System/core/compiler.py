from core.models import FinalOutput

class OutputCompiler:
    def __init__(self):
        pass

    def process(self, final_data: dict) -> dict:
        """
        Valide la structure des données finales avec Pydantic pour garantir
        le respect strict du OUTPUT FINAL OBLIGATOIRE.
        """
        try:
            validated = FinalOutput(**final_data)
            return validated.model_dump()
        except Exception as e:
            raise ValueError(f"Erreur de compilation JSON: {e}")
