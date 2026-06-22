#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${LOG_DIR:-/private/tmp/insightos-logs}"
BACKEND_VENV="${BACKEND_VENV:-/private/tmp/insightos-backend-venv}"

mkdir -p "$LOG_DIR"

is_up() {
  curl -fsS --max-time 2 "$1" >/dev/null 2>&1
}

if is_up "http://localhost:8000/health"; then
  echo "Backend already running on http://localhost:8000"
else
  if [ ! -f "$BACKEND_VENV/bin/activate" ]; then
    echo "Backend virtual environment not found at $BACKEND_VENV"
    echo "Install backend dependencies first, or run Docker Compose when Docker is available."
    exit 1
  fi

  (
    cd "$ROOT_DIR/backend"
    # shellcheck disable=SC1091
    source "$BACKEND_VENV/bin/activate"
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$LOG_DIR/backend.log" 2>&1 &
    echo $! > "$LOG_DIR/backend.pid"
  )
  echo "Started backend on http://localhost:8000"
fi

if is_up "http://localhost:3000/"; then
  echo "Frontend already running on http://localhost:3000"
else
  (
    cd "$ROOT_DIR/frontend"
    nohup env npm_config_cache=/private/tmp/insightos-npm-cache npm run preview:local > "$LOG_DIR/frontend.log" 2>&1 &
    echo $! > "$LOG_DIR/frontend.pid"
  )
  echo "Started frontend preview on http://localhost:3000"
fi

echo "Logs: $LOG_DIR"
