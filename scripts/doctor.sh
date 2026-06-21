#!/usr/bin/env bash
set -euo pipefail

missing=0

check_command() {
  local name="$1"
  local install_hint="$2"

  if command -v "$name" >/dev/null 2>&1; then
    printf "OK   %s: %s\n" "$name" "$(command -v "$name")"
  else
    printf "MISS %s: %s\n" "$name" "$install_hint"
    missing=1
  fi
}

echo "InsightOS startup check"
echo

check_command docker "Install and start Docker Desktop, then reopen your terminal."
check_command node "Install Node.js 22+ if you want to run the frontend outside Docker."
check_command npm "Install npm if you want to run the frontend outside Docker."
check_command python3 "Install Python 3.12+ if you want to run the backend outside Docker."

echo

if command -v docker >/dev/null 2>&1; then
  if docker compose version >/dev/null 2>&1; then
    printf "OK   docker compose: %s\n" "$(docker compose version --short)"
  else
    echo "MISS docker compose: Docker is installed, but the Compose plugin is unavailable."
    missing=1
  fi
fi

echo

if [ "$missing" -eq 0 ]; then
  echo "All required startup commands are available."
  echo "Next command: docker compose up --build"
else
  echo "One or more startup requirements are missing."
  echo "For this project, Docker Desktop is required for the one-command local stack."
fi

exit "$missing"
