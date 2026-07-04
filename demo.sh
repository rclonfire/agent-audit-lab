#!/usr/bin/env bash
# One-command demo: run the full audit against the seeded agent.
set -euo pipefail
cd "$(dirname "$0")"

python3 audit/run_audit.py
echo
echo "Open the report: reports/sample-audit.md"
