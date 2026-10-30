"""Put the agent and audit modules on sys.path the same way the scripts do.

pytest also adds the repository root, and `agent/` is a directory, so an
unqualified `import agent` would see a namespace package instead of
`agent/agent.py`. Inserting the script directories first preserves the
import style used by `python3 agent/chat.py` and `python3 audit/run_audit.py`.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for entry in (ROOT / "audit", ROOT / "agent"):
    path = str(entry)
    if path in sys.path:
        sys.path.remove(path)
    sys.path.insert(0, path)
