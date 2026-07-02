$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    Write-Host "Environnement Python introuvable: $pythonExe" -ForegroundColor Red
    Write-Host "Installez les dependances puis relancez." -ForegroundColor Yellow
    exit 1
}

$cloudflared = Get-Command cloudflared -ErrorAction SilentlyContinue
if (-not $cloudflared) {
    Write-Host "cloudflared n'est pas installe." -ForegroundColor Red
    Write-Host "Installez-le avec: winget install --id Cloudflare.cloudflared -e" -ForegroundColor Yellow
    exit 1
}

Write-Host "Demarrage du quiz (Streamlit) dans une nouvelle fenetre..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$projectRoot'; & '$pythonExe' -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true --server.enableCORS false --server.enableXsrfProtection false"

Start-Sleep -Seconds 2

Write-Host "Demarrage du tunnel securise Cloudflare dans une nouvelle fenetre..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$projectRoot'; cloudflared tunnel --url http://localhost:8501"

Write-Host "" 
Write-Host "Termine. 2 fenetres ont ete ouvertes:" -ForegroundColor Green
Write-Host "1) Streamlit (serveur du quiz)" -ForegroundColor Green
Write-Host "2) Cloudflared (lien HTTPS public)" -ForegroundColor Green
Write-Host "" 
Write-Host "Copiez le lien https://*.trycloudflare.com affiche dans la fenetre Cloudflared." -ForegroundColor Yellow
