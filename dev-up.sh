#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
SEED=0

usage() {
  cat <<'EOF'
Usage: ./dev-up.sh [--seed]

Starts PostgreSQL, applies migrations, then runs the API on :8000 and the
frontend on :5500. Press Ctrl+C to stop the API and frontend. The database
keeps running and keeps its data (use `docker compose down` to stop it).

  --seed   Run scripts/seed_test_db.py after migrations
EOF
}

for arg in "$@"; do
  case "$arg" in
    --seed) SEED=1 ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Unknown argument: $arg. Use --help." >&2
      exit 1
      ;;
  esac
done

port_in_use() {
  local port="$1"
  if command -v nc >/dev/null 2>&1; then
    nc -z 127.0.0.1 "$port" >/dev/null 2>&1
    return $?
  fi
  if command -v lsof >/dev/null 2>&1; then
    lsof -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
    return $?
  fi
  (echo >/dev/tcp/127.0.0.1/"$port") >/dev/null 2>&1
}

assert_port_free() {
  local port="$1"
  local owner="$2"
  if port_in_use "$port"; then
    echo "Port $port is already in use. Stop the process using it before starting $owner." >&2
    exit 1
  fi
}

require_cmd() {
  local name="$1"
  local hint="$2"
  if ! command -v "$name" >/dev/null 2>&1; then
    echo "$name was not found. $hint" >&2
    exit 1
  fi
}

require_cmd docker "Install Docker and make sure the daemon is running."
require_cmd uv "Install uv: https://docs.astral.sh/uv/getting-started/installation/"
require_cmd python3 "Install Python 3.13."

assert_port_free 8000 "the API (uvicorn)"
assert_port_free 5500 "the frontend static server"

echo "Starting PostgreSQL..."
docker compose up -d --wait

echo "Applying migrations..."
(
  cd "$BACKEND"
  uv run alembic upgrade head
  if [[ "$SEED" -eq 1 ]]; then
    echo "Seeding the database..."
    uv run python -m scripts.seed_test_db
  fi
)

API_PID=""
FRONTEND_PID=""

cleanup() {
  if [[ -n "$FRONTEND_PID" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    kill "$FRONTEND_PID" 2>/dev/null || true
    wait "$FRONTEND_PID" 2>/dev/null || true
  fi
  if [[ -n "$API_PID" ]] && kill -0 "$API_PID" 2>/dev/null; then
    kill "$API_PID" 2>/dev/null || true
    wait "$API_PID" 2>/dev/null || true
  fi
  echo "API and frontend stopped. Database is still running."
}

trap cleanup EXIT INT TERM

echo "Starting API on http://127.0.0.1:8000 ..."
(
  cd "$BACKEND"
  uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
) &
API_PID=$!

echo "Starting frontend on http://127.0.0.1:5500 ..."
(
  cd "$FRONTEND"
  python3 -m http.server 5500 --bind 127.0.0.1
) &
FRONTEND_PID=$!

echo
echo "Local stack is up."
echo "  API       http://127.0.0.1:8000/health"
echo "  Frontend  http://127.0.0.1:5500/"
echo "  Docs API  http://127.0.0.1:8000/docs"
echo
echo "Press Ctrl+C to stop the API and frontend."
echo "The database stays up. Stop it with: docker compose down"
echo

wait
