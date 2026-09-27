#!/usr/bin/env bash
# Start the KittenConnect dev server, clearing any stale process on the port first.
set -euo pipefail

PORT="${PORT:-8000}"
cd "$(dirname "$0")"

# Kill anything already listening on the port (prevents "Address already in use").
if lsof -tiTCP:"$PORT" >/dev/null 2>&1; then
  echo "Freeing port $PORT (killing stale process)..."
  lsof -tiTCP:"$PORT" | xargs kill -9 2>/dev/null || true
  sleep 1
fi

# Use the project venv's uvicorn so we never fall back to system Python.
echo "Starting uvicorn on http://127.0.0.1:$PORT (docs at /docs) — Ctrl+C to stop"
exec ./venv/bin/uvicorn main:app --reload --port "$PORT"
