#!/usr/bin/env bash
# One-command demo.
#   ./demo.sh         deterministic audit, no API key
#   ./demo.sh --live  Anthropic API if ANTHROPIC_API_KEY is set, else the claude CLI
set -euo pipefail
cd "$(dirname "$0")"

usage() {
  cat <<'EOF'
Usage: ./demo.sh [--live]

  (default)  Run the 11-probe audit with the deterministic offline model.
             No API key. Rewrites reports/sample-audit.md.
  --live     Use ANTHROPIC_API_KEY if it is set, otherwise the local claude
             CLI. Fails if neither is available. FERN_LLM=api or FERN_LLM=cli
             is honored; FERN_LLM=mock is not (that is the default mode).
EOF
}

case "${1:-}" in
  "")
    export FERN_LLM=mock
    unset FERN_LLM_REQUESTED
    ;;
  --live)
    export FERN_LLM_REQUESTED=live
    if [[ -z "${FERN_LLM:-}" || "${FERN_LLM}" == "mock" ]]; then
      export FERN_LLM=auto
    fi
    ;;
  -h|--help)
    usage
    exit 0
    ;;
  *)
    echo "Unknown argument: $1" >&2
    usage >&2
    exit 2
    ;;
esac

python3 audit/run_audit.py
echo
echo "Open the report: reports/sample-audit.md"
