#!/usr/bin/env bash
# Lean auth-less live smoke against LIVE_BASE_URL (default https://gethosteva.com).
# Intended for workflow_dispatch only — not every PR.
set -euo pipefail

BASE_URL="${LIVE_BASE_URL:-https://gethosteva.com}"
BASE_URL="${BASE_URL%/}"

check() {
  local path="$1"
  local optional="${2:-0}"
  local url="${BASE_URL}${path}"
  local code
  code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 30 -L "$url" || true)"
  if [[ "$code" =~ ^2 ]]; then
    echo "OK  ${code}  ${path}"
    return 0
  fi
  if [[ "$optional" == "1" && "$code" == "404" ]]; then
    echo "SKIP ${code}  ${path} (optional, not present)"
    return 0
  fi
  echo "FAIL ${code}  ${path}  (${url})" >&2
  return 1
}

echo "smoke_live against ${BASE_URL}"
check "/"
check "/login"
check "/features"
check "/about"
check "/health" 1

echo "smoke_live passed"
