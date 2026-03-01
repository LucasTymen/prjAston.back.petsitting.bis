# Sprint déploiement Contabo — Job Search Agent

**Règle absolue :** Ne jamais arrêter, supprimer ni modifier les containers ou services **SquidResearch**. Toutes les commandes ciblent uniquement le projet Job Search Agent dans `/opt/job_search_agent`.

---

## Rôles et responsabilités

| Rôle | Responsabilité |
|------|----------------|
| **Chef de projet** | Valider les étapes, ordre des commandes, rollback si besoin |
| **DevOps** | Clé SSH, déploiement (tar/scp), `docker compose` dans `/opt/job_search_agent` uniquement |
| **Pentester** | Vérifier que les commandes ne ciblent pas SquidResearch ; revue des accès SSH |
| **Ingénieur système / réseau** | Vérifier `docker ps` avant/après, intégrité des containers existants |

---

## Phase 1 — Clé SSH Contabo (DevOps + Ingé système)

### 1.1 Générer une clé dédiée (optionnel, évite d’écraser une clé existante)

```powershell
# PowerShell (Windows) — clé dédiée Contabo
$keyPath = "$env:USERPROFILE\.ssh\id_rsa_contabo"
if (-not (Test-Path $keyPath)) {
    ssh-keygen -t ed25519 -f $keyPath -N '""' -C "contabo-job-agent"
    Write-Host "Cle generee : $keyPath et $keyPath.pub"
}
Get-Content "$keyPath.pub"
```

Sous WSL/Linux :

```bash
KEY=~/.ssh/id_ed25519_contabo
test -f "$KEY" || ssh-keygen -t ed25519 -f "$KEY" -N "" -C "contabo-job-agent"
cat "${KEY}.pub"
```

### 1.2 Récupérer / installer la clé sur Contabo

- **Option A — Déjà en place :** tu as une clé et tu te connectes avec `ssh root@173.249.4.106`. Rien à faire.
- **Option B — Premier accès (mot de passe) :** connecte-toi une fois avec le mot de passe fourni par Contabo, puis ajoute la clé :

```bash
ssh root@173.249.4.106 "mkdir -p .ssh && cat >> .ssh/authorized_keys" < "$HOME/.ssh/id_ed25519_contabo.pub"
```

- **Option C — Contabo Cloud Panel :** dans le panel Contabo, section SSH Keys, ajouter le contenu de `id_ed25519_contabo.pub` pour le VPS concerné.

### 1.3 Tester la connexion

```powershell
# Windows (clé par défaut)
ssh root@173.249.4.106 "echo OK"

# Ou avec la clé dédiée
ssh -i $env:USERPROFILE\.ssh\id_rsa_contabo root@173.249.4.106 "echo OK"
```

```bash
# WSL/Linux avec clé dédiée
ssh -i ~/.ssh/id_ed25519_contabo root@173.249.4.106 "echo OK"
```

---

## Phase 2 — Vérification pré-déploiement (Pentester + Ingé système)

**À exécuter sur le serveur** (après `ssh root@173.249.4.106`) pour état des lieux :

```bash
# Lister TOUS les containers (pour preuve qu’on ne touche pas à SquidResearch)
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"

# Noter les noms des containers SquidResearch (ex. squid_*, *squid*, etc.)
docker ps -a --format "{{.Names}}" | grep -i squid || true
```

Conserver cette liste : après déploiement, les mêmes containers doivent toujours être présents et en état **Up**.

---

## Phase 3 — Déploiement (DevOps)

Toutes les commandes ci-dessous sont **non destructives** pour le reste du serveur : elles ne font que créer/mettre à jour le répertoire `/opt/job_search_agent` et les containers **job_search_agent** et **job_agent_cron**.

### 3.1 Depuis ta machine (PowerShell, depuis le dossier du projet)

```powershell
cd "C:\Users\Lucas\.gemini\antigravity\brain\c718aa18-28de-4cd5-9403-f4be6c1ae8db\Job_Search_Agent_System"

# Tar + SSH (exclut .env, venv, .git, *.db, *.log)
tar --exclude=.env --exclude=venv --exclude=.git --exclude=__pycache__ --exclude=.pytest_cache --exclude=htmlcov --exclude="*.db" --exclude="*.log" -cvf - . | ssh root@173.249.4.106 "mkdir -p /opt/job_search_agent && cd /opt/job_search_agent && tar -xvf -"
```

Si `tar` n’est pas dispo sous PowerShell, utiliser le script existant :

```powershell
.\scripts\deploy.ps1
```

### 3.2 Créer le `.env` sur le serveur (une seule fois)

Se connecter en SSH puis :

```bash
cd /opt/job_search_agent
nano .env
```

Coller (et adapter) :

```env
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile
PROFILE_JSON_PATH=resources/cv_base_datas_pour_candidatures.json
GMAIL_USER=...
GMAIL_APP_PASSWORD=...
```

Sauvegarder (Ctrl+O, Entrée, Ctrl+X). **Ne jamais** pousser le fichier `.env` par SCP/tar.

---

## Phase 4 — Lancement des containers (DevOps + Chef de projet)

**Important :** exécuter `docker compose` **uniquement** depuis `/opt/job_search_agent`. Ainsi, seuls les services de ce projet sont gérés (job_agent, job_agent_cron), pas SquidResearch.

### 4.1 Sur le serveur (SSH)

```bash
cd /opt/job_search_agent

# Vérifier que le fichier compose ne référence que notre stack
grep -E "container_name|image:" docker-compose.yml

# Build et démarrage (uniquement nos 2 services)
docker compose up -d --build

# Vérifier que seuls nos containers sont créés/modifiés
docker ps --filter "name=job_agent" --format "table {{.Names}}\t{{.Status}}"
```

### 4.2 Contrôle post-déploiement (Pentester + Ingé système)

```bash
# SquidResearch doit être inchangé (même liste qu’en Phase 2)
docker ps -a --format "{{.Names}}" | grep -i squid || true

# Nos containers doivent être Up
docker ps --filter "name=job_agent"
```

---

## Phase 5 — Tests non destructifs (DevOps)

```bash
cd /opt/job_search_agent

# Dry-run cron (aucune candidature réelle, aucun envoi)
docker exec job_agent_cron python -m scheduler.cron_runner --sources wttj --dry-run --max 2

# Dry-run relances
docker exec job_agent_cron python -m scheduler.followup_runner --dry-run

# Logs (consultation seule)
docker exec job_agent_cron tail -20 /app/logs/cron.log
docker exec job_agent_cron tail -20 /app/logs/followup.log
```

---

## Commandes interdites (toute l’équipe)

- `docker stop squid*` ou tout arrêt de container dont le nom contient `squid`
- `docker compose down` ou `docker compose down -v` **en dehors** de `/opt/job_search_agent` (et jamais sur le projet SquidResearch)
- `docker system prune -a` sans filtre excluant explicitement les containers SquidResearch
- Toute modification des fichiers ou services dans un répertoire autre que `/opt/job_search_agent` (sauf `.ssh` pour la clé)

---

## Rollback (Chef de projet)

Si besoin d’arrêter uniquement Job Search Agent :

```bash
cd /opt/job_search_agent
docker compose down
```

Cela n’affecte que les containers **job_search_agent** et **job_agent_cron**. SquidResearch n’est pas impacté.

---

## Résumé des commandes chaînées (copier-coller)

**Sur ta machine (une fois la clé SSH OK) :**

```powershell
cd "C:\Users\Lucas\.gemini\antigravity\brain\c718aa18-28de-4cd5-9403-f4be6c1ae8db\Job_Search_Agent_System"
tar --exclude=.env --exclude=venv --exclude=.git --exclude=__pycache__ --exclude=.pytest_cache --exclude=htmlcov --exclude="*.db" --exclude="*.log" -cvf - . | ssh root@173.249.4.106 "mkdir -p /opt/job_search_agent && cd /opt/job_search_agent && tar -xvf -"
```

**Puis en SSH sur le serveur :**

```bash
cd /opt/job_search_agent && docker compose up -d --build && docker exec job_agent_cron python -m scheduler.cron_runner --sources wttj --dry-run --max 2
```

Après avoir créé le `.env` à la main sur le serveur (Phase 3.2).
