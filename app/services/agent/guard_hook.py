"""PreToolUse hook: deny destructive Bash commands even under bypassPermissions.

``bypassPermissions`` (the only headless mode that works on Windows) disables
Claude Code's allow/deny lists, so the agent could otherwise run any shell
command. When ``AIFOS_AGENT_ENFORCE_GUARDRAIL_HOOK=true`` the runner writes a
``.claude/settings.json`` into the job folder that points Claude Code's
``PreToolUse`` hook (matcher ``Bash``) at this script.

Claude Code pipes the tool input as JSON on stdin. We reuse the single source of
truth in :func:`guardrail.is_command_blocked`:

- a destructive match -> exit code 2 (Claude Code blocks the call, shows stderr)
- anything else        -> exit code 0 (allowed)

We fail *open* on unparseable input so a schema change can never wedge the agent;
the deny list still fires for every command we can read (the normal case).
"""

import json
import sys
from pathlib import Path

# Make the app package importable no matter which cwd Claude Code runs us from.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from app.services.agent.guardrail import is_command_blocked  # noqa: E402


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # fail open: never block the agent on a parsing quirk
    command = (payload.get("tool_input") or {}).get("command", "")
    if command and is_command_blocked(command):
        print(
            f"AIFOS guardrail blocked a destructive command: {command!r}",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
