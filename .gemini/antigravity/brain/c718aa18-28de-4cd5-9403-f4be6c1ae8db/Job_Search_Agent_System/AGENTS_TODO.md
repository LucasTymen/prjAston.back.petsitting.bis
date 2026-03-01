# TODO partagée — Agents IA

> Liste des tâches en attente. Mettre à jour après chaque action.

---

## Priorité — Accès distant Telegram
- [x] Bot Telegram — contrôle Job Search Agent depuis n'importe où (`scheduler/telegram_bot.py`)
- [x] Whitelist `TELEGRAM_ALLOWED_IDS` + rate limiting + audit log
- [x] Service `job_telegram` dans docker-compose

---

## Phase 2 — LLM & Matching
- [x] Créer `core/llm_client.py` — wrapper OpenAI (via .env)
- [x] Intégrer embeddings + cosine similarity dans `MatchingEngine` (via OpenAI)
- [x] Tests unitaires pour le nouveau scoring (via `process_test_offers.py`)
- [x] ScraperOffre : brancher `extract_with_llm()` sur OpenAI

---

## Phase 3 — PDF & Refinement
- [ ] Créer `agents/cv_pdf.py` — Générateur de CV PDF (ATS friendly + style)
- [ ] Mettre à jour `agents/generator.py` — Raffinement des messages par LLM
- [ ] Mettre à jour `agents/drafting.py` — Support des pièces jointes (IMAP)
- [ ] Mettre à jour `core/orchestrator.py` — Intégration PDF + Draft attachment

---

## Phase 4 — Dashboard FastAPI
- [ ] Créer `api/app.py` — FastAPI minimal
- [ ] Route `GET /applications` — liste candidatures
- [ ] Route `GET /cv/{id}` — télécharger le PDF généré
- [ ] Route `POST /retry/{id}` — re-générer avec ajustements

---

## Améliorations futures (backlog)
- [ ] EntrepriseScraper : URL dynamique depuis l'offre
- [ ] JobQueue : paramètres de recherche via `.env`
- [x] Script cron J+4 / J+10 pour relances auto — followup_runner.py
