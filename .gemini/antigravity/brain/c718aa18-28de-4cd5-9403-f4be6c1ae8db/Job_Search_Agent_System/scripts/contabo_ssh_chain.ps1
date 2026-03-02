# Script PowerShell : enchaînement CLI pour déploiement Contabo
# Usage : .\scripts\contabo_ssh_chain.ps1
# Prérequis : SSH opérationnel (root@173.249.4.106), clé ou mot de passe
# Règle : ne jamais cibler SquidResearch.

$ErrorActionPreference = "Stop"
$Server = "root@173.249.4.106"
$RemotePath = "/opt/job_search_agent"
$KeyPath = "$env:USERPROFILE\.ssh\id_ed25519_contabo"
$KeyPathRsa = "$env:USERPROFILE\.ssh\id_rsa_contabo"

function Ssh-Invoke {
    param([string]$Command)
    $sshArgs = @()
    if (Test-Path $KeyPath) { $sshArgs = @("-i", $KeyPath) }
    elseif (Test-Path $KeyPathRsa) { $sshArgs = @("-i", $KeyPathRsa) }
    & ssh $sshArgs $Server $Command
}

Write-Host "[1/4] Verification SSH..." -ForegroundColor Cyan
Ssh-Invoke "echo OK"
Write-Host "[2/4] Etat des lieux containers (SquidResearch ne doit pas etre touche)..." -ForegroundColor Cyan
Ssh-Invoke "docker ps -a --format 'table {{.Names}}\t{{.Status}}'"

Write-Host "[3/4] Deploiement tar vers $RemotePath ..." -ForegroundColor Cyan
$TarExclude = "--exclude=.env --exclude=venv --exclude=.git --exclude=__pycache__ --exclude=.pytest_cache --exclude=htmlcov --exclude=*.db --exclude=*.log"
Set-Location (Join-Path $PSScriptRoot "..")
$tarAvailable = Get-Command tar -ErrorAction SilentlyContinue
if ($tarAvailable) {
    $cmd = "tar $TarExclude -cvf - . | ssh $Server `"mkdir -p $RemotePath && cd $RemotePath && tar -xvf -`""
    Invoke-Expression $cmd
} else {
    Write-Host "tar non trouve. Utiliser: .\scripts\deploy.ps1 pour SCP" -ForegroundColor Yellow
    & "$PSScriptRoot\deploy.ps1"
}

Write-Host "[4/4] Sur le serveur: build + up (uniquement job_search_agent)..." -ForegroundColor Cyan
Ssh-Invoke "cd $RemotePath && docker compose up -d --build"

Write-Host "Containers job_agent apres deploy:" -ForegroundColor Cyan
Ssh-Invoke "docker ps --filter name=job_agent --format 'table {{.Names}}\t{{.Status}}'"

Write-Host "Rappel: creer .env sur le serveur si pas deja fait: ssh $Server `"cd $RemotePath && nano .env`"" -ForegroundColor Yellow
Write-Host "Test dry-run: ssh $Server `"docker exec job_agent_cron python -m scheduler.cron_runner --dry-run --max 2`"" -ForegroundColor Yellow
