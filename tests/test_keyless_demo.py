"""The commands a fresh clone is told to run."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "data" / "store.json"


def _env(**extra):
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)
    env.pop("FERN_LLM", None)
    env.pop("FERN_LLM_REQUESTED", None)
    env.pop("FERN_REPORT_DIR", None)
    # Keep the test from picking up a developer-installed claude binary.
    env["PATH"] = "/usr/bin:/bin"
    env.update(extra)
    return env


def _run(args, env, cwd=ROOT, input_text=None):
    return subprocess.run(
        args,
        cwd=cwd,
        env=env,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def test_demo_sh_is_keyless_and_reproduces_every_probe(tmp_path):
    before = STORE.read_bytes()
    env = _env(FERN_REPORT_DIR=str(tmp_path), ANTHROPIC_API_KEY="should-not-be-used", FERN_LLM="api")
    proc = _run(["./demo.sh"], env)
    assert proc.returncode == 0, proc.stderr
    assert "Backend: mock (deterministic, no API key)" in proc.stdout
    assert "Seeded defects reproduced: 6/6" in proc.stdout
    assert "Expected-good probes passing: 5/5" in proc.stdout
    report = (tmp_path / "sample-audit.md").read_text()
    assert report.count("**Status:** REPRODUCED") == 6
    assert "NOT REPRODUCED" not in report
    assert "10,000" in report
    assert "handoff denied" in report
    assert "cancel-reschedule-appointment.md" in report
    assert STORE.read_bytes() == before


def test_demo_sh_live_without_credentials_exits_2():
    proc = _run(["./demo.sh", "--live"], _env())
    assert proc.returncode == 2
    assert "ANTHROPIC_API_KEY" in proc.stderr
    assert "REPRODUCED" not in proc.stdout


def test_demo_sh_live_api_without_a_key_exits_2():
    proc = _run(["./demo.sh", "--live"], _env(FERN_LLM="api"))
    assert proc.returncode == 2
    assert "requires ANTHROPIC_API_KEY" in proc.stderr


def test_demo_sh_rejects_unknown_args_and_prints_help():
    bad = _run(["./demo.sh", "--cloud"], _env())
    assert bad.returncode == 2
    help_proc = _run(["./demo.sh", "--help"], _env())
    assert help_proc.returncode == 0
    assert "No API key." in help_proc.stdout


def test_raw_audit_command_is_also_keyless(tmp_path):
    env = _env(FERN_REPORT_DIR=str(tmp_path), ANTHROPIC_API_KEY="should-not-be-used")
    proc = _run([sys.executable, "audit/run_audit.py"], env)
    assert proc.returncode == 0, proc.stderr
    assert "Backend: mock (deterministic, no API key)" in proc.stdout


def test_scripted_chat_shows_the_unwritten_email_and_the_false_paid_status():
    proc = _run([sys.executable, "agent/chat.py", "--demo"], _env(ANTHROPIC_API_KEY="nope"))
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout
    assert "Backend: mock (deterministic, no API key)" in out
    assert "$59" in out
    assert "updated to blue.fox@rowan.example" in out
    assert "still dana@rowanplumbing.example" in out
    assert "INV-1042A" in out and "paid" in out
    assert "\033[" not in out  # captured stdout is not a TTY, so no color codes


def test_interactive_chat_exits_on_eof():
    proc = _run([sys.executable, "agent/chat.py"], _env(), input_text="What are your support hours?\n")
    assert proc.returncode == 0, proc.stderr
    assert "Monday" in proc.stdout
    assert "Mountain" in proc.stdout


def test_chat_live_without_credentials_exits_2():
    proc = _run([sys.executable, "agent/chat.py", "--live"], _env())
    assert proc.returncode == 2
    assert "ANTHROPIC_API_KEY" in proc.stderr


def _readme_sample_blocks():
    readme = (ROOT / "README.md").read_text()
    start = readme.index("## Sample output")
    end = readme.index("## Live model")
    parts = readme[start:end].split("```")
    blocks = []
    index = 1
    while index < len(parts):
        body = parts[index]
        if body.startswith("\n"):
            body = body[1:]
        blocks.append(body)
        index += 2
    return blocks


def test_readme_samples_match_the_commands():
    demo_block, chat_block = _readme_sample_blocks()
    demo = _run(["./demo.sh"], _env())
    chat = _run([sys.executable, "agent/chat.py", "--demo"], _env())
    assert demo.returncode == 0, demo.stderr
    assert chat.returncode == 0, chat.stderr
    assert demo.stdout == demo_block
    assert chat.stdout == chat_block


def test_readme_quickstart_does_not_require_a_key_or_install():
    readme = (ROOT / "README.md").read_text()
    start = readme.index("## Quickstart")
    end = readme.index("\n## ", start + 4)
    section = readme[start:end]
    assert "./demo.sh" in section
    assert "ANTHROPIC_API_KEY" not in section
    assert "pip install" not in section
    assert "Intercom" not in readme
    assert "Zendesk" not in readme
    assert "Kubernetes" not in readme
    assert "docs/demo.gif" in readme
    gif = ROOT / "docs" / "demo.gif"
    assert gif.is_file()
    assert gif.stat().st_size > 1000


def test_agent_and_audit_do_not_read_the_ticket_corpus():
    blob = "\n".join(
        path.read_text()
        for folder in ("agent", "audit")
        for path in (ROOT / folder).glob("*.py")
    )
    assert "tickets" not in blob
    assert len(list((ROOT / "kb").glob("*.md"))) == 14
    probes = (ROOT / "audit" / "probes.json").read_text()
    assert probes.count('"id":') == 11
