# Roadmap — Agents IA (Antigravity Bridge)

## Architecture & Coordination
- **Source de vérité :** `resources/cv_base_datas_pour_candidatures.json` (ATV Strict).
- **Coordination :** Triplet `AGENTS_LOG.md`, `AGENTS_ROADMAP.md`, `AGENTS_TODO.md`.
- **LLM :** OpenAI `gpt-4o-mini` (via `core/llm_client.py`).

## Workflow Actuel
1. **Cron principal :** `--mode both` = scan + matching + filtre POSTULER + pipeline full (CV/LM/emails)
2. **Cron relances :** quotidien 8h — `followup_runner` J+4/J+10 via Gmail drafts
3. **Découverte :** requêtes persona-driven (`persona_queries.py`)
4. **Matching :** déterministe Python (MatchingEngine), seuils POSTULER >= 60

## Prochaines Étapes (Phase 3 : PDF & Refinement)
- **PDF Engine :** `agents/cv_pdf.py` pour générer des CV professionnels et ATS-friendly.
- **Message Polishing :** Raffinement des corps d'email par LLM pour plus de personnalisation.
- **Attachments :** Support des pièces jointes dans le drafting IMAP.

## Règles de Développement
- **Principe Antigravity :** Ne jamais inventer de données non présentes dans le JSON de base.
- **Atomicité :** Chaque agent doit être testable isolément.
- **Documentation :** Mettre à jour les logs après chaque modification structurelle.
