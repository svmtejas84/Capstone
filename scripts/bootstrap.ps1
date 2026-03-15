Write-Host "Starting local infrastructure..."
docker compose -f infra/docker-compose.yml up -d

Write-Host "Backend dependencies (requires active venv)..."
Push-Location backend
pip install -r requirements.txt
Pop-Location

Write-Host "Frontend dependencies..."
Push-Location frontend
npm install
Pop-Location

Write-Host "Bootstrap complete."
