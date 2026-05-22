#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IBKR_BIN="${ROOT}/.venv/bin/ibkr"

PROFILE="${1:-ib-a-paper}"
GATEWAY="${2:-ib-a}"
SYMBOL="${3:-AAPL}"
QTY="${4:-1}"

echo "[1/3] gateway health"
if ! "${IBKR_BIN}" gateway health "${GATEWAY}" --json; then
  exit 1
fi

echo
echo "[2/3] connect test"
"${IBKR_BIN}" connect test --profile "${PROFILE}" --json

echo
echo "[3/3] buy preview"
"${IBKR_BIN}" buy "${SYMBOL}" "${QTY}" --preview --profile "${PROFILE}" --json
