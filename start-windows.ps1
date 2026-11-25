$ErrorActionPreference='Stop'
Set-Location $PSScriptRoot
if (!(Get-Command docker -ErrorAction SilentlyContinue)) { throw 'Docker CLI not installed. Install Docker Desktop.' }
docker info *> $null
if ($LASTEXITCODE -ne 0) { throw 'Docker engine is not running. Open Docker Desktop, then retry.' }
if (!(Test-Path '.env')) {
  Copy-Item '.env.example' '.env'
  $raw = Get-Content '.env' -Raw
  $secret = -join ((1..60) | ForEach-Object { ('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789').ToCharArray() | Get-Random })
  $raw = $raw.Replace('REPLACE_WITH_LONG_RANDOM_SECRET',$secret)
  [System.IO.File]::WriteAllText((Join-Path $PSScriptRoot '.env'), $raw, (New-Object System.Text.UTF8Encoding($false)))
  Write-Host 'Created .env. Add OPENAI_API_KEY to enable generative answers; extractive/SQL mode works without it.'
}
Write-Host 'Building and starting Docker services. First install may download Python packages and embedding models.'
docker compose up --build -d
if ($LASTEXITCODE -ne 0) { throw 'Docker build/start failed. Run docker compose logs to inspect.' }
Write-Host 'Web UI: http://localhost:5173'
Write-Host 'API docs: http://localhost:8000/docs'
Write-Host 'Demo admin: admin@demo.retail / RetailDemo2026! (change before public deployment)'
Write-Host 'Indexing runs automatically after startup; inspect Docker logs and Document Library.'
