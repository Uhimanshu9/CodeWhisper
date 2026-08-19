#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_DIR="$ROOT_DIR/voice_coding_agent"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
COMPOSE_FILE="$AGENT_DIR/docker-compose.yml"
DASHBOARD_PORT="${VERSION_PREVIEW_PORT:-4090}"
DASHBOARD_URL="http://127.0.0.1:$DASHBOARD_PORT"
RUNTIME_DIR="$ROOT_DIR/.runtime/version_preview"
DASHBOARD_LOG="$RUNTIME_DIR/dashboard.log"

START_GREEN=$'\033[38;5;46m'
START_DIM_GREEN=$'\033[38;5;71m'
START_RED=$'\033[38;5;203m'
START_RESET=$'\033[0m'

print_green() {
  printf '%s%s%s\n' "$START_GREEN" "$*" "$START_RESET"
}

print_dim_green() {
  printf '%s%s%s\n' "$START_DIM_GREEN" "$*" "$START_RESET"
}

print_red() {
  printf '%s%s%s\n' "$START_RED" "$*" "$START_RESET"
}

if [[ ! -x "$PYTHON_BIN" ]]; then
  print_red "Missing project virtual environment: $PYTHON_BIN"
  print_red "Create it with: python3 -m venv .venv && .venv/bin/pip install -r voice_coding_agent/requirement.txt"
  exit 1
fi

if [[ ! -f "$AGENT_DIR/.env" ]]; then
  print_red "Missing configuration file: $AGENT_DIR/.env"
  print_red "Create it with: cp voice_coding_agent/.env.example voice_coding_agent/.env"
  print_red "Then add your OPENAI_API_KEY before starting the project."
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  print_red "Docker is required to start MongoDB."
  exit 1
fi

print_green "Starting MongoDB..."
docker compose --ansi never -f "$COMPOSE_FILE" up -d 2>&1 |
  while IFS= read -r line; do print_dim_green "$line"; done
print_green "MongoDB is online."

dashboard_pid=""

cleanup() {
  local exit_code=$?
  trap - EXIT INT TERM

  if [[ -n "$dashboard_pid" ]] && kill -0 "$dashboard_pid" 2>/dev/null; then
    kill "$dashboard_pid" 2>/dev/null || true
  fi

  wait "$dashboard_pid" 2>/dev/null || true
  printf '\n'
  print_green "CodeWhisper stopped. MongoDB is still running."
  exit "$exit_code"
}

trap cleanup EXIT INT TERM

if curl -fsS --max-time 2 "$DASHBOARD_URL/api/project" >/dev/null 2>&1; then
  print_green "Dashboard is online at $DASHBOARD_URL"
else
  occupied_pids="$(lsof -tiTCP:"$DASHBOARD_PORT" -sTCP:LISTEN 2>/dev/null || true)"
  for pid in $occupied_pids; do
    process_cwd="$(lsof -a -p "$pid" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p')"
    if [[ "$process_cwd" == "$AGENT_DIR" ]]; then
      print_dim_green "Restarting stale CodeWhisper dashboard (PID $pid)..."
      kill "$pid" 2>/dev/null || true
      for _ in {1..10}; do
        kill -0 "$pid" 2>/dev/null || break
        sleep 0.1
      done
    else
      print_red "Port $DASHBOARD_PORT is already occupied by another process (PID $pid)."
      print_red "Stop that process or set VERSION_PREVIEW_PORT to a free port."
      exit 1
    fi
  done

  if lsof -nP -iTCP:"$DASHBOARD_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    print_red "Could not stop the stale dashboard on port $DASHBOARD_PORT."
    exit 1
  fi

  mkdir -p "$RUNTIME_DIR"
  (
    cd "$AGENT_DIR"
    VERSION_PREVIEW_PORT="$DASHBOARD_PORT" exec "$PYTHON_BIN" -m version_preview.app >>"$DASHBOARD_LOG" 2>&1
  ) &
  dashboard_pid=$!

  for _ in {1..30}; do
    curl -fsS --max-time 1 "$DASHBOARD_URL/api/project" >/dev/null 2>&1 && break
    sleep 0.1
  done
  if ! curl -fsS --max-time 1 "$DASHBOARD_URL/api/project" >/dev/null 2>&1; then
    print_red "Dashboard did not become ready. See $DASHBOARD_LOG"
    exit 1
  fi
  print_green "Dashboard is online at $DASHBOARD_URL"
fi

print_green "CodeWhisper is ready."
if [[ -t 1 && "${CODEWHISPER_NO_CLEAR:-0}" != "1" ]]; then
  sleep 0.35
  printf '\033[2J\033[H'
fi

set +e
(
  cd "$AGENT_DIR"
  CODEWHISPER_DASHBOARD_URL="$DASHBOARD_URL" exec "$PYTHON_BIN" audio_test.py
)
agent_status=$?
set -e

exit "$agent_status"
