"""Interactive chat with the Fernwheel demo agent.

    python3 agent/chat.py

Shows retrieval and tool activity inline (dim), which is exactly what you
want visible in a recorded demo.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent import SupportAgent

DIM, RESET, BOLD = "\033[2m", "\033[0m", "\033[1m"


def main():
    print(f"{BOLD}Fern — Fernwheel support (demo){RESET}")
    print(f"{DIM}Fictional company, synthetic data. Ctrl-C to exit.{RESET}\n")
    agent = SupportAgent()
    while True:
        try:
            msg = input(f"{BOLD}you:{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not msg:
            continue
        seen = len(agent.events)
        reply = agent.ask(msg)
        for ev in agent.events[seen:]:
            if ev["type"] == "retrieval":
                files = ", ".join(f'{f["file"]}({f["score"]})' for f in ev["files"]) or "none"
                print(f"{DIM}  retrieved: {files}{RESET}")
            elif ev["type"] == "tool_call":
                print(f"{DIM}  tool: {ev['tool']}({ev['args']}) -> {ev['result']}{RESET}")
        print(f"{BOLD}fern:{RESET} {reply}\n")


if __name__ == "__main__":
    main()
