$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    Write-Host "Environnement Python introuvable: $pythonExe" -ForegroundColor Red
    Write-Host "Installez d'abord les dependances, puis relancez." -ForegroundColor Yellow
    exit 1
}

# Get the primary IPv4 address used for outbound traffic.
$primaryIp = (Get-NetRoute -DestinationPrefix "0.0.0.0/0" |
    Sort-Object RouteMetric |
    ForEach-Object {
        Get-NetIPAddress -InterfaceIndex $_.InterfaceIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue |
            Where-Object { $_.IPAddress -notlike "169.254.*" -and $_.IPAddress -notlike "127.*" }
    } |
    Select-Object -First 1 -ExpandProperty IPAddress)

if (-not $primaryIp) {
    Write-Host "Impossible de detecter une IP locale IPv4." -ForegroundColor Red
    Write-Host "Verifiez que le Wi-Fi est connecte, puis relancez." -ForegroundColor Yellow
    exit 1
}

Write-Host "" 
Write-Host "Lien iPhone (meme Wi-Fi):" -ForegroundColor Green
Write-Host "http://$primaryIp:8501" -ForegroundColor Cyan
Write-Host "" 
Write-Host "Si iPhone ne charge pas: autorisez Python/Streamlit dans le pare-feu Windows (reseau prive)." -ForegroundColor Yellow
Write-Host "" 
Write-Host "Demarrage du serveur quiz..." -ForegroundColor Green

& $pythonExe -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true --server.enableCORS false --server.enableXsrfProtection false
