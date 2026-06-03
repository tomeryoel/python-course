# Build React frontend into static/dist
Set-Location $PSScriptRoot\frontend
npm install
npm run build
Write-Host "Done. Output: static/dist"
