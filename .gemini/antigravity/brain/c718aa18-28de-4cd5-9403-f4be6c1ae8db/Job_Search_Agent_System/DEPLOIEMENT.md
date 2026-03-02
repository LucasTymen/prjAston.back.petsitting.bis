# Déploiement Contabo — Job Search Agent

**Règle :** ne jamais toucher aux containers SquidResearch.

---

## 0. Premier commit et push (bon emplacement)

Le dépôt Git a sa racine **au-dessus** du projet (ex. `C:\Users\Lucas`). Tu dois être **dans le dossier du projet** pour n’ajouter que les fichiers Job_Search_Agent_System.

**Vérifier l’emplacement :**
```bash
pwd
# Doit se terminer par .../Job_Search_Agent_System
git rev-parse --show-toplevel
# Affiche la racine du repo (souvent ton home)
```

**Commit uniquement le projet (sans toucher au README ou autres dossiers du repo) :**
```bash
# Toujours depuis Job_Search_Agent_System
git add .
git status
# Vérifier : seuls AGENTS_*, agents/, core/, scheduler/, scripts/, tests/ doivent être listés (pas ../../../../../README.md ni dossiers home)
git commit -m "Job Search Agent: séquence J0→J2→J1→J2, CV structure, directives rédaction, placeholders, nommage PJ, Telegram /pipeline + chatbot. AGENTS_LOG + ROADMAP."
git push
```

**Lien avec la prod Contabo :** la prod **n’est pas** un `git pull` sur le serveur. Elle est alimentée par **tar + SSH** (ou le script PowerShell) depuis ta machine. Donc :
1. **Commit + push** = sauvegarde dans le dépôt distant (origin).
2. **Déploiement prod** = lancer le script de déploiement **depuis ce même dossier** (après commit) pour envoyer le code vers Contabo. Le serveur reçoit une copie du contenu du dossier, pas un clone Git.

Après un push, pour mettre la prod à jour : exécuter `.\scripts\contabo_ssh_chain.ps1` (PowerShell) ou la commande Tar + SSH du §2, **depuis Job_Search_Agent_System**.

---

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
| Principal | `0 */2 * * *` | `cron_runner --mode both --sources wttj,francetravail,indeed,hellowork,dogfinance,meteojob,glassdoor,linkedin,apec,manpower,adecco` |
| Relances | `0 8 * * *` | `followup_runner` |

**Mode both :** scan + matching → filtre POSTULER uniquement → pipeline full (CV, LM, emails) → persistance `applications.db` et `storage/outputs/`

**Followup :** relances J+2, J+4, J+7, J+9 (séquence J0→J2→J1→J1→J2) via brouillons Gmail (lit `applications.db`)

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

# Relances J+2, J+4, J+7, J+9
python -m scheduler.followup_runner --dry-run
python -m scheduler.followup_runner
```
