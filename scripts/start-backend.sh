#!/usr/bin/env bash
# Start the VectCutAPI backend that the MCP server talks to.
# The MCP server is useless without this running.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend/VectCutAPI"

if [ ! -x "$BACKEND/.venv/bin/python" ]; then
  echo "Backend not installed. Run:" >&2
  echo "  git clone https://github.com/sun-guannan/VectCutAPI.git '$BACKEND'" >&2
  echo "  cd '$BACKEND' && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
  echo "  cp config.json.example config.json" >&2
  exit 1
fi

if curl -fsS -m 3 -o /dev/null "http://localhost:9001/get_mask_types" 2>/dev/null; then
  echo "Backend already running on :9001"
  exit 0
fi

cd "$BACKEND"
echo "Starting VectCutAPI on http://localhost:9001 (Ctrl-C to stop)"
exec .venv/bin/python capcut_server.py
