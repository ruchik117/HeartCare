#!/usr/bin/env bash
# HeartCare MVP — one command: FastAPI + Next.js
# Usage: bash run.sh [backend_port] [frontend_port]
#   Defaults: backend 8001, frontend 3000 (8000 is often taken; override as needed)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
BACKEND_PORT="${1:-${BACKEND_PORT:-8001}}"
FRONTEND_PORT="${2:-${FRONTEND_PORT:-3000}}"
PY="$HERE/../.venv/bin/python"

if [ ! -x "$PY" ]; then
  echo "Missing ../.venv — run: cd .. && uv venv && uv pip install -r heartcare-web/requirements-api.txt"
  exit 1
fi

# Clear our own leftovers (never touches other users' processes)
pkill -f "[n]ext-server \(v" 2>/dev/null || true
pkill -f "[u]vicorn api\.main" 2>/dev/null || true
sleep 1

"$PY" -m uvicorn api.main:app --port "$BACKEND_PORT" --app-dir "$HERE" &
BACK=$!
(cd "$HERE/web" && NEXT_PUBLIC_API_URL="http://localhost:$BACKEND_PORT" npm run dev -- --port "$FRONTEND_PORT") &
FRONT=$!
trap 'kill $BACK $FRONT 2>/dev/null' INT TERM EXIT
echo "backend  http://localhost:$BACKEND_PORT  docs: http://localhost:$BACKEND_PORT/docs"
echo "frontend http://localhost:$FRONTEND_PORT"
wait
