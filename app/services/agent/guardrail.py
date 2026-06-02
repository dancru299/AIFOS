"""Safety guardrail for the autonomous Claude Code worker.

The agent needs a real shell (install deps, run tests, build) but must not run
destructive or out-of-folder commands. We enforce this with Claude Code's
permission flags, which are honored reliably in headless mode:

- ``--allowedTools`` auto-runs the safe tool set (incl. Bash) without prompts.
- ``--disallowedTools`` hard-denies dangerous shell command prefixes (deny wins).
- the runner also confines file edits to the job folder (``cwd`` + ``--add-dir``).

``is_command_blocked`` mirrors the deny policy in plain Python for unit testing.
"""

import re

# Auto-approved tools (Claude Code syntax: "Bash(<prefix> *)"). Bash is allowed
# broadly so the agent can install deps and run tests, but dangerous command
# prefixes below are explicitly denied (deny wins). File tools are confined to
# the job folder by the runner (cwd + --add-dir).
ALLOWED_TOOLS: tuple[str, ...] = (
    "Read",
    "Write",
    "Edit",
    "MultiEdit",
    "Glob",
    "Grep",
    "TodoWrite",
    "NotebookEdit",
    "Bash(python *)",
    "Bash(python3 *)",
    "Bash(py *)",
    "Bash(pip *)",
    "Bash(pip3 *)",
    "Bash(pytest *)",
    "Bash(ruff *)",
    "Bash(mypy *)",
    "Bash(node *)",
    "Bash(npm *)",
    "Bash(npx *)",
    "Bash(yarn *)",
    "Bash(pnpm *)",
    "Bash(go *)",
    "Bash(cargo *)",
    "Bash(make *)",
    "Bash(php *)",
    "Bash(composer *)",
    "Bash(ls *)",
    "Bash(cat *)",
    "Bash(echo *)",
    "Bash(pwd *)",
    "Bash(mkdir *)",
    "Bash(touch *)",
    "Bash(cp *)",
    "Bash(mv *)",
    "Bash(grep *)",
    "Bash(find *)",
    "Bash(head *)",
    "Bash(tail *)",
    "Bash(git add *)",
    "Bash(git commit *)",
    "Bash(git status *)",
    "Bash(git diff *)",
    "Bash(git log *)",
    "Bash(git init *)",
    "Bash(git checkout *)",
    "Bash(git branch *)",
)

# Dangerous shell command prefixes that must be denied (space-star syntax).
DISALLOWED_TOOL_RULES: tuple[str, ...] = (
    "Bash(sudo *)",
    "Bash(rm *)",
    "Bash(rmdir *)",
    "Bash(del *)",
    "Bash(git push *)",
    "Bash(git remote *)",
    "Bash(ssh *)",
    "Bash(scp *)",
    "Bash(sftp *)",
    "Bash(curl *)",
    "Bash(wget *)",
    "Bash(shutdown *)",
    "Bash(reboot *)",
    "Bash(mkfs *)",
    "Bash(dd *)",
    "Bash(npm publish *)",
    "Bash(format *)",
)

# Plain-Python mirror of the deny policy (for unit tests / defense-in-depth).
BLOCKED_PATTERNS: tuple[str, ...] = (
    r"\brm\s+-",
    r"\b(rmdir|del)\s+/[sq]",
    r"\bsudo\b",
    r"\b(shutdown|reboot|halt|poweroff)\b",
    r"\bmkfs\b",
    r"\bdd\s+if=",
    r"\bgit\s+push\b",
    r"\bgit\s+remote\b",
    r"\b(ssh|scp|sftp)\b",
    r"\bnpm\s+publish\b",
    r"\bformat\s+[a-z]:",
)

_COMPILED = tuple(re.compile(p, re.IGNORECASE) for p in BLOCKED_PATTERNS)


def is_command_blocked(command: str) -> bool:
    """True if a shell command matches a destructive/out-of-bounds pattern."""
    return any(pattern.search(command) for pattern in _COMPILED)
