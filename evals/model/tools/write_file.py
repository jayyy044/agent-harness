from pathlib import Path

# ASCII on purpose: non-ASCII is the harness eval's job, and the model rewrites
# '-' as U+2011 on its own, which would fail this case for a reason that isn't the tool
SCRIPT = """#!/bin/sh
echo "deploying $APP to '$HOST'"
printf 'done\\n'
"""


def check(d, out, history):
    f = Path(d) / "deploy.sh"
    content_ok = f.exists() and f.read_text().rstrip("\n") == SCRIPT.rstrip("\n")
    # without this, a bash heredoc that happens to quote correctly is a false pass
    used_write_file = any(
        c["function"]["name"] == "write_file"
        for m in history
        for c in (m.get("tool_calls") or [])
    )
    return content_ok and used_write_file


CASES = [
    {
        "name": "write_file_exact_content",
        "setup": lambda d: None,
        "prompt": f"Create deploy.sh containing exactly this script:\n\n{SCRIPT}",
        "check": check,
    },
]
