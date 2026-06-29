#!/usr/bin/env bash
# Quickstart script for macOS/Linux/WSL
set -euo pipefail

echo "=== HTANC AI - HFT Trading Engine ==="
echo ""

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example — edit it to configure your brokers."
else
    echo ".env already exists."
fi

echo ""
echo "Starting services in paper mode..."
docker compose up --build
