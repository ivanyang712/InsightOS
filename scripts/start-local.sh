#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${LOG_DIR:-/private/tmp/insightos-logs}"
BACKEND_VENV="${BACKEND_VENV:-/private/tmp/insightos-backend-venv}"

mkdir -p "$LOG_DIR"

is_up() {
  curl -fsS --max-time 2 "$1" >/dev/null 2>&1
}

kill_port() {
  local port="$1"
  local pids
  pids="$(lsof -ti "tcp:$port" 2>/dev/null || true)"
  if [ -n "$pids" ]; then
    echo "Stopping stale process on port $port"
    # shellcheck disable=SC2086
    kill $pids 2>/dev/null || true
    sleep 1
    pids="$(lsof -ti "tcp:$port" 2>/dev/null || true)"
    if [ -n "$pids" ]; then
      # shellcheck disable=SC2086
      kill -9 $pids 2>/dev/null || true
    fi
  fi
}

has_fresh_frontend() {
  curl -fsS --max-time 2 "http://localhost:3000/" 2>/dev/null \
    | grep -q "InsightOS 投研工作台体验"
}

if is_up "http://localhost:8000/health"; then
  echo "Backend already running on http://localhost:8000"
else
  kill_port 8000
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

if has_fresh_frontend; then
  echo "Frontend already running on http://localhost:3000"
else
  kill_port 3000
  (
    cd "$ROOT_DIR/frontend"
    nohup env npm_config_cache=/private/tmp/insightos-npm-cache npm run dev -- --port 3000 > "$LOG_DIR/frontend.log" 2>&1 &
    echo $! > "$LOG_DIR/frontend.pid"
  )
  echo "Started frontend on http://localhost:3000"
fi

echo "Logs: $LOG_DIR"
