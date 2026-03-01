#!/bin/bash
# A executer SUR le serveur Contabo (apres SSH).
# Non destructif : ne touche qu'a /opt/job_search_agent et aux containers job_agent*.
# Ne jamais arreter/modifier les containers SquidResearch.

set -e
PROJECT_DIR="/opt/job_search_agent"

log_ok()   { echo "[OK] $*"; }
log_warn() { echo "[WARN] $*"; }
log_err()  { echo "[ERR] $*"; }

check_squid_untouched() {
  docker ps -a --format "{{.Names}}" | grep -i squid || true
}

if [ ! -f "$PROJECT_DIR/docker-compose.yml" ]; then
  log_err "Absent: $PROJECT_DIR/docker-compose.yml"
  exit 1
fi

cd "$PROJECT_DIR"
log_ok "Repertoire: $PROJECT_DIR"
echo "--- Avant ---"
check_squid_untouched

log_ok "docker compose up -d --build"
docker compose up -d --build

echo "--- Containers job_agent ---"
docker ps --filter "name=job_agent" --format "table {{.Names}}\t{{.Status}}"
echo "--- Apres (SquidResearch inchange) ---"
check_squid_untouched

if docker ps --format "{{.Names}}" | grep -q job_agent_cron; then
  log_ok "Dry-run cron..."
  docker exec job_agent_cron python -m scheduler.cron_runner --sources wttj,francetravail --dry-run --max 2 || true
  log_ok "Dry-run followup..."
  docker exec job_agent_cron python -m scheduler.followup_runner --dry-run || true
fi
log_ok "Fin deploiement securise."
