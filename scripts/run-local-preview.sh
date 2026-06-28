#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${LOG_DIR:-/private/tmp/insightos-logs}"
BACKEND_VENV="${BACKEND_VENV:-/private/tmp/insightos-backend-venv}"
BACKEND_PORT="${BACKEND_PORT:-8001}"
FRONTEND_PORT="${FRONTEND_PORT:-3001}"
BACKEND_URL="http://localhost:$BACKEND_PORT"

mkdir -p "$LOG_DIR"

is_up() {
  curl -fsS --max-time 2 "$1" >/dev/null 2>&1
}

wait_for_http() {
  local url="$1"
  local label="$2"
  local attempts="${3:-60}"
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

cleanup() {
  if [ -n "${backend_pid:-}" ]; then
    kill "$backend_pid" 2>/dev/null || true
  fi
  if [ -n "${frontend_pid:-}" ]; then
    kill "$frontend_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

if [ ! -f "$BACKEND_VENV/bin/activate" ]; then
  echo "Backend virtual environment not found at $BACKEND_VENV"
  exit 1
fi

(
  cd "$ROOT_DIR/backend"
  # shellcheck disable=SC1091
  source "$BACKEND_VENV/bin/activate"
  uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT"
) > "$LOG_DIR/backend-$BACKEND_PORT.log" 2>&1 &
backend_pid=$!

wait_for_http "$BACKEND_URL/health" "Backend"
if ! curl -fsS --max-time 2 "$BACKEND_URL/openapi.json" | grep -q "/api/research/company/{ticker}"; then
  echo "Backend is reachable, but the single-stock research endpoint is missing."
  exit 1
fi

(
  cd "$ROOT_DIR/frontend"
  NEXT_PUBLIC_API_BASE_URL="$BACKEND_URL" npm run build
  NEXT_PUBLIC_API_BASE_URL="$BACKEND_URL" npm run start -- --port "$FRONTEND_PORT"
) > "$LOG_DIR/frontend-$FRONTEND_PORT.log" 2>&1 &
frontend_pid=$!

wait_for_http "http://localhost:$FRONTEND_PORT/" "Frontend"

echo "InsightOS preview is ready:"
echo "- Frontend: http://localhost:$FRONTEND_PORT"
echo "- Backend:  $BACKEND_URL"
echo "- Logs:     $LOG_DIR"

wait
