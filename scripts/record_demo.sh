#!/usr/bin/env bash
# Rebuild docs/demo.cast and docs/demo.gif from a real keyless ./demo.sh run.
# Requires asciinema and agg (https://github.com/asciinema/agg). Not used by CI.
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v asciinema >/dev/null || ! command -v agg >/dev/null; then
  echo "asciinema and agg must be on PATH" >&2
  exit 1
fi

mkdir -p docs
export TERM="${TERM:-xterm-256color}"
if [[ "$TERM" == "dumb" ]]; then
  export TERM=xterm-256color
fi
env -u ANTHROPIC_API_KEY -u FERN_LLM -u FERN_LLM_REQUESTED \
  asciinema rec --overwrite -q --cols 100 --rows 24 \
  -c "printf '%s\n' '\$ ./demo.sh'; ./demo.sh" \
  docs/demo.cast

python3 scripts/pace_cast.py docs/demo.cast

agg --font-size 16 --theme monokai --fps-cap 12 --speed 1 \
  docs/demo.cast docs/demo.gif

echo "Wrote docs/demo.cast and docs/demo.gif"
