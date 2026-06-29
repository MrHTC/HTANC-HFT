#! /usr/bin/env pwsh
# Quickstart script for Windows
Write-Host "=== HTANC AI - HFT Trading Engine ===" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example — edit it to configure your brokers." -ForegroundColor Yellow
} else {
    Write-Host ".env already exists." -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting services in paper mode..." -ForegroundColor Cyan
docker compose up --build
