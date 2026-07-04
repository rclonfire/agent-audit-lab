"""Model backend. Two paths, no third-party dependencies:

1. ANTHROPIC_API_KEY set  -> Anthropic Messages API over urllib.
2. Otherwise              -> the local `claude` CLI in headless print mode,
                             which uses whatever auth Claude Code already has.
"""

import json
import os
import subprocess
import urllib.request

MODEL = os.environ.get("FERN_MODEL", "claude-haiku-4-5-20251001")
API_URL = "https://api.anthropic.com/v1/messages"


def complete(prompt: str) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return _api(prompt, key)
    return _cli(prompt)


def _api(prompt: str, key: str) -> str:
    body = json.dumps({
        "model": MODEL,
        "max_tokens": 1024,
        "temperature": 0,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(API_URL, data=body, headers={
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.load(resp)
    return "".join(b.get("text", "") for b in data.get("content", []))


def _cli(prompt: str) -> str:
    proc = subprocess.run(
        ["claude", "-p", "--model", MODEL],
        input=prompt, capture_output=True, text=True, timeout=180,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {proc.stderr.strip()[:400]}")
    return proc.stdout.strip()
