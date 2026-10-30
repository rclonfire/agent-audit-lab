"""Model backend. No third-party packages.

Unset FERN_LLM (and FERN_LLM=mock) uses deterministic local replies. A key
in the environment does not change that. Opt in to a live model:

1. FERN_LLM=mock   -> deterministic local replies. No network.
2. FERN_LLM=api    -> Anthropic Messages API. Requires ANTHROPIC_API_KEY.
3. FERN_LLM=cli    -> the local `claude` CLI in headless print mode.
4. FERN_LLM=auto   -> api if ANTHROPIC_API_KEY is set, else cli if `claude`
                      is on PATH, else mock.

./demo.sh and ./demo.sh --live are the wrappers. --live selects auto unless
FERN_LLM is already api or cli.
"""

import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request

from mock_llm import complete_mock

DEFAULT_MODEL = "claude-haiku-4-5-20251001"
API_URL = "https://api.anthropic.com/v1/messages"

_MOCK = {"mock", "offline", "fixture"}
_API = {"api", "anthropic"}
_CLI = {"cli", "claude"}
_AUTO = {"auto", ""}


def model_name() -> str:
    return os.environ.get("FERN_MODEL", DEFAULT_MODEL)


def backend_name() -> str:
    mode = os.environ.get("FERN_LLM", "mock").strip().lower()
    if mode in _AUTO:
        if os.environ.get("ANTHROPIC_API_KEY"):
            return "api"
        if shutil.which("claude"):
            return "cli"
        return "mock"
    if mode in _MOCK:
        return "mock"
    if mode in _API:
        return "api"
    if mode in _CLI:
        return "cli"
    raise RuntimeError(
        f"Unknown FERN_LLM={mode!r}. Use mock, api, cli, or auto."
    )


def backend_label() -> str:
    name = backend_name()
    if name == "mock":
        return "mock (deterministic, no API key)"
    if name == "api":
        return f"anthropic messages API ({model_name()})"
    if name == "cli":
        return f"claude CLI ({model_name()})"
    return name


def assert_backend_ready() -> None:
    name = backend_name()
    if os.environ.get("FERN_LLM_REQUESTED") == "live" and name == "mock":
        raise RuntimeError(
            "Live mode needs ANTHROPIC_API_KEY or the claude CLI on PATH. "
            "Run ./demo.sh with no arguments for the keyless demo."
        )
    if name == "api" and not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("FERN_LLM=api requires ANTHROPIC_API_KEY.")
    if name == "cli" and shutil.which("claude") is None:
        raise RuntimeError("FERN_LLM=cli requires the claude CLI on PATH.")


def complete(prompt: str) -> str:
    assert_backend_ready()
    name = backend_name()
    if name == "mock":
        return complete_mock(prompt)
    if name == "api":
        return _api(prompt, os.environ["ANTHROPIC_API_KEY"])
    return _cli(prompt)


def _api(prompt: str, key: str) -> str:
    body = json.dumps({
        "model": model_name(),
        "max_tokens": 1024,
        "temperature": 0,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(API_URL, data=body, headers={
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:400]
        raise RuntimeError(f"Anthropic API HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Anthropic API request failed: {exc.reason}") from exc
    return "".join(b.get("text", "") for b in data.get("content", []))


def _cli(prompt: str) -> str:
    if shutil.which("claude") is None:
        raise RuntimeError("FERN_LLM=cli requires the claude CLI on PATH.")
    try:
        proc = subprocess.run(
            ["claude", "-p", "--model", model_name()],
            input=prompt, capture_output=True, text=True, timeout=180,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("FERN_LLM=cli requires the claude CLI on PATH.") from exc
    if proc.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {proc.stderr.strip()[:400]}")
    return proc.stdout.strip()
