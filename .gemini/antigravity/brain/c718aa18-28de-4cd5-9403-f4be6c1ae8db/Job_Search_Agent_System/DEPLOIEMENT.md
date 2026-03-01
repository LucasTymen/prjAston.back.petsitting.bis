# Déploiement Contabo — Job Search Agent

**Règle :** ne jamais toucher aux containers SquidResearch.

**Scripts :**
- Depuis ta machine : `.\scripts\contabo_ssh_chain.ps1` (PowerShell) ou Tar + SSH ci-dessous
- Sur le serveur après SSH : `bash /opt/job_search_agent/scripts/contabo_safe_deploy.sh`

---

## 1. Avant déploiement — Exclure .env

Le fichier `.env` contient tes clés. **Ne jamais le copier via SCP.**

## 2. Transfert — Tar + SSH (recommandé)

```powershell
cd C:\Users\Lucas\.gemini\antigravity\brain\c718aa18-28de-4cd5-9403-f4be6c1ae8db\Job_Search_Agent_System

tar --exclude=.env --exclude=venv --exclude=.git --exclude=__pycache__ --exclude=.pytest_cache --exclude=htmlcov --exclude="*.db" --exclude="*.log" -cvf - . | ssh root@173.249.4.106 "mkdir -p /opt/job_search_agent && cd /opt/job_search_agent && tar -xvf -"
```

## 3. Sur le serveur — .env

```bash
ssh root@173.249.4.106
cd /opt/job_search_agent
nano .env
```

Contenu minimal du .env :
```env
# LLM (obligatoire)
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile
PROFILE_JSON_PATH=resources/cv_base_datas_pour_candidatures.json

# Telegram Bot (obligatoire pour /scan, /status, etc.)
TELEGRAM_BOT_TOKEN=7xxxxxxxxx:AAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TELEGRAM_ALLOWED_IDS=584739201,2025051518

# Optionnel
# OPENAI_API_KEY=sk-...
# DB_PATH=/app/storage/applications.db
# LOG_PATH=/app/logs/cron.log
```

```bash
# 4. Vérifier SquidResearch avant build
docker ps | grep squid

# 5. Builder et lancer (cron + bot Telegram)
docker compose up -d --build

# 6. Test manuel
docker exec job_agent_cron python -m scheduler.cron_runner --sources wttj,francetravail --dry-run --max 3

# 7. Logs
docker exec job_agent_cron tail -f /app/logs/cron.log
docker logs -f job_telegram_bot
```

## Services Docker

| Service | Container | Rôle |
|---------|-----------|------|
| job_telegram | job_telegram_bot | Bot Telegram (/scan, /status, /logs…) |
| cron | job_agent_cron | Cron toutes les 2h + followup quotidien |
| job_agent | job_agent | Worker (si besoin) |

## Cron

| Cron | Fréquence | Commande |
|------|-----------|----------|
| Principal | `0 */2 * * *` | `cron_runner --mode both --sources wttj,francetravail,indeed,hellowork,dogfinance,meteojob,glassdoor,linkedin,apec` |
| Relances | `0 8 * * *` | `followup_runner` |

**Mode both :** scan + matching → filtre POSTULER uniquement → pipeline full (CV, LM, emails) → persistance `applications.db` et `storage/outputs/`

**Followup :** relances J+4 et J+10 via brouillons Gmail (lit `applications.db`)

## Si le run freeze ou bloque

- **Playwright** : `networkidle` remplacé par `load` pour éviter blocage sur SPA avec polling infini
- **LLM** : timeout 60s sur les appels Groq/OpenAI
- **Gmail** : utiliser un **App Password** (pas le mot de passe standard) — Google bloque parfois les connexions IMAP "anormales"
- **Rate limit** : si Groq/OpenAI limite, réduire `--max` (ex. `--max 3`)

```bash
# Modes disponibles
python -m scheduler.cron_runner --mode scan   # JobScanner uniquement (CSV ou JSON)
python -m scheduler.cron_runner --mode full   # Pipeline complet sans pré-filtrage
python -m scheduler.cron_runner --mode both   # Scan + filtre POSTULER + pipeline (défaut cron)
python -m scheduler.cron_runner --mode both --scan-format json

# Relances J+4/J+10
python -m scheduler.followup_runner --dry-run
python -m scheduler.followup_runner
```
