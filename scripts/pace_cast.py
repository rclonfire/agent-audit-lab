#!/usr/bin/env python3
"""Re-time an asciinema v2 cast so each recorded line stays readable.

The bytes are the recording's. This only changes when each chunk is shown.
"""

import json
import sys


def pace(path: str, delay: float = 0.48, hold: float = 2.4) -> None:
    raw_lines = open(path, encoding="utf-8").read().splitlines()
    if not raw_lines:
        raise SystemExit(f"{path} is empty")
    header = json.loads(raw_lines[0])
    if header.get("version") != 2:
        raise SystemExit(f"{path} is not an asciinema v2 cast")
    chunks = []
    for line in raw_lines[1:]:
        if not line.strip():
            continue
        _time, kind, data = json.loads(line)
        if kind == "o" and data:
            chunks.append(data)
    text = "".join(chunks)
    parts = []
    buf = ""
    for ch in text:
        buf += ch
        if ch == "\n":
            parts.append(buf)
            buf = ""
    if buf:
        parts.append(buf)
    if not parts:
        raise SystemExit(f"{path} has no output")

    events = [json.dumps(header, ensure_ascii=False)]
    clock = 0.0
    for part in parts:
        events.append(json.dumps([round(clock, 3), "o", part], ensure_ascii=False))
        clock += delay
    events.append(json.dumps([round(clock + hold, 3), "o", ""]))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(events) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: pace_cast.py <file.cast>")
    pace(sys.argv[1])
