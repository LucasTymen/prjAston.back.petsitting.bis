# Deploiement Job Search Agent vers Contabo
# Usage : .\scripts\deploy.ps1
# IMPORTANT : .env n'est PAS copie — creer manuellement sur le serveur

$SERVER = "root@173.249.4.106"
$REMOTE_PATH = "/opt/job_search_agent"

Write-Host "Exclusion : .env, venv, .git, __pycache__" -ForegroundColor Yellow
Write-Host "Lancement SCP..." -ForegroundColor Cyan

# SCP : copier dossiers et fichiers essentiels (sans .env)
$items = @(
    "core", "agents", "scheduler", "storage", "resources", "tests", "scripts",
    "main.py", "Dockerfile", "docker-compose.yml", "requirements.txt", "crontab",
    ".dockerignore", ".env.example"
)
$items += Get-ChildItem -Filter "AGENTS_*.md" | ForEach-Object { $_.Name }

$itemList = ($items | ForEach-Object { if (Test-Path $_) { $_ } }) -join " "
if ($itemList) {
    scp -r $itemList "${SERVER}:${REMOTE_PATH}/"
} else {
    scp -r core agents scheduler storage resources main.py Dockerfile docker-compose.yml requirements.txt crontab .dockerignore .env.example "${SERVER}:${REMOTE_PATH}/"
}

Write-Host "SCP termine." -ForegroundColor Green
Write-Host "Rappel : creer .env sur le serveur : ssh $SERVER `"cd $REMOTE_PATH && nano .env`"" -ForegroundColor Yellow
