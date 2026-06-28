#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${LOG_DIR:-/private/tmp/insightos-logs}"
BACKEND_VENV="${BACKEND_VENV:-/private/tmp/insightos-backend-venv}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

mkdir -p "$LOG_DIR"

is_up() {
  curl -fsS --max-time 2 "$1" >/dev/null 2>&1
}

stop_pid_file() {
  local pid_file="$1"
  if [ -f "$pid_file" ]; then
    local pid
    pid="$(tr -d '[:space:]' < "$pid_file")"
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      sleep 1
      if kill -0 "$pid" 2>/dev/null; then
        kill -9 "$pid" 2>/dev/null || true
      fi
    fi
    rm -f "$pid_file"
  fi
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

wait_for_http() {
  local url="$1"
  local label="$2"
  local attempts="${3:-30}"
  local attempt
  for attempt in $(seq 1 "$attempts"); do
    if is_up "$url"; then
      return 0
    fi
    sleep 1
  done
  echo "$label did not become ready at $url"
  return 1
}

backend_has_research_endpoint() {
  local port="$1"
  curl -fsS --max-time 2 "http://localhost:$port/openapi.json" \
    | grep -q "/api/research/company/{ticker}"
}

start_backend_on_port() {
  local port="$1"
  kill_port "$port"
  (
    cd "$ROOT_DIR/backend"
    # shellcheck disable=SC1091
    source "$BACKEND_VENV/bin/activate"
    nohup uvicorn app.main:app --host 0.0.0.0 --port "$port" > "$LOG_DIR/backend.log" 2>&1 &
    echo $! > "$LOG_DIR/backend.pid"
  )
  echo "Started backend on http://localhost:$port"
  wait_for_http "http://localhost:$port/health" "Backend"
  backend_has_research_endpoint "$port"
}

stop_pid_file "$LOG_DIR/backend.pid"
stop_pid_file "$LOG_DIR/frontend.pid"

if [ ! -f "$BACKEND_VENV/bin/activate" ]; then
  echo "Backend virtual environment not found at $BACKEND_VENV"
  echo "Install backend dependencies first, or run Docker Compose when Docker is available."
  exit 1
fi

if ! start_backend_on_port "$BACKEND_PORT"; then
  if [ "$BACKEND_PORT" = "8000" ]; then
    echo "Port 8000 is serving an older API that could not be replaced; using 8001 for this preview."
    BACKEND_PORT="8001"
    start_backend_on_port "$BACKEND_PORT"
  else
    echo "Backend started, but the single-stock research endpoint is missing."
    echo "See $LOG_DIR/backend.log"
    exit 1
  fi
fi
BACKEND_URL="http://localhost:$BACKEND_PORT"

kill_port "$FRONTEND_PORT"
rm -rf "$ROOT_DIR/frontend/.next"
(
  cd "$ROOT_DIR/frontend"
  NEXT_PUBLIC_API_BASE_URL="$BACKEND_URL" npm run build > "$LOG_DIR/frontend-build.log" 2>&1
  nohup env NEXT_PUBLIC_API_BASE_URL="$BACKEND_URL" npm_config_cache=/private/tmp/insightos-npm-cache npm run start -- --port "$FRONTEND_PORT" > "$LOG_DIR/frontend.log" 2>&1 &
  echo $! > "$LOG_DIR/frontend.pid"
)
echo "Started frontend on http://localhost:$FRONTEND_PORT"
wait_for_http "http://localhost:$FRONTEND_PORT/" "Frontend"
if ! curl -fsS --max-time 2 "http://localhost:$FRONTEND_PORT/" | grep -q "单只股票研究主链路"; then
  echo "Frontend started, but the single-stock research UI is missing."
  echo "See $LOG_DIR/frontend.log and $LOG_DIR/frontend-build.log"
  exit 1
fi

echo "Backend URL: $BACKEND_URL"
echo "Logs: $LOG_DIR"
