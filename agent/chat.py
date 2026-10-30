"""Interactive chat with the Fernwheel demo agent.

    python3 agent/chat.py          # deterministic offline model, no API key
    python3 agent/chat.py --demo   # the four turns from DEMO-SCRIPT.md
    python3 agent/chat.py --live   # Anthropic API or the local claude CLI

Shows retrieval and tool activity inline, which is what you want visible
in a recorded demo.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

DEMO_TURNS = [
    "How much does the Crew plan cost per technician?",
    "Hi, my login is dana@rowanplumbing.example. Please change my notification email to blue.fox@rowan.example.",
    "Can you read back what notification email is on my account right now?",
    "Can you check whether invoice INV-1042A is paid?",
]


def _configure(argv):
    if "--live" in argv:
        os.environ["FERN_LLM_REQUESTED"] = "live"
        if os.environ.get("FERN_LLM", "mock") in ("", "mock"):
            os.environ["FERN_LLM"] = "auto"
    else:
        os.environ["FERN_LLM"] = "mock"
        os.environ.pop("FERN_LLM_REQUESTED", None)


def _usage():
    print(
        "Usage: python3 agent/chat.py [--demo] [--live]\n"
        "  (default)  deterministic offline model, no API key\n"
        "  --demo     print four scripted turns and exit\n"
        "  --live     ANTHROPIC_API_KEY, or the claude CLI if there is no key",
        file=sys.stderr,
    )


def main(argv=None):
    argv = list(sys.argv if argv is None else argv)
    unknown = [a for a in argv[1:] if a not in {"--demo", "--live", "--help", "-h"}]
    if unknown or "--help" in argv or "-h" in argv:
        _usage()
        return 2 if unknown else 0

    _configure(argv)

    from agent import SupportAgent
    from llm import assert_backend_ready, backend_label

    try:
        assert_backend_ready()
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    color = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
    dim, reset, bold = ("\033[2m", "\033[0m", "\033[1m") if color else ("", "", "")

    print(f"{bold}Fern — Fernwheel support (demo){reset}")
    print(f"{dim}Backend: {backend_label()}{reset}")
    if "--demo" in argv:
        print(f"{dim}Scripted turns from DEMO-SCRIPT.md.{reset}\n")
    else:
        print(f"{dim}Fictional company, synthetic data. Ctrl-C to exit.{reset}\n")

    agent = SupportAgent()

    def show(msg):
        print(f"{bold}you:{reset} {msg}")
        seen = len(agent.events)
        reply = agent.ask(msg)
        for ev in agent.events[seen:]:
            if ev["type"] == "retrieval":
                files = ", ".join(f'{f["file"]}({f["score"]})' for f in ev["files"]) or "none"
                print(f"{dim}  retrieved: {files}{reset}")
            elif ev["type"] == "tool_call":
                print(f"{dim}  tool: {ev['tool']}({ev['args']}) -> {ev['result']}{reset}")
        print(f"{bold}fern:{reset} {reply}\n")

    if "--demo" in argv:
        for msg in DEMO_TURNS:
            show(msg)
        return 0

    while True:
        try:
            msg = input(f"{bold}you:{reset} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not msg:
            continue
        show(msg)


if __name__ == "__main__":
    raise SystemExit(main())
