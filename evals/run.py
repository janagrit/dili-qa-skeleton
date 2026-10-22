"""Run agent-eval with Claude Code pinned to a model (Opus vs Sonnet).

agent-eval's built-in claude-code adapter can't pick a model and gives the
headless agent no edit permission, so this registers two adapters that can,
then hands off to the normal agent-eval CLI:

    python evals/run.py run --tasks evals/suite.yaml --agents opus,sonnet --runs 3
"""

import asyncio
import json
import os
import subprocess
import time
from pathlib import Path

from agenteval import cli
from agenteval.adapters import ADAPTERS
from agenteval.adapters.base import AgentAdapter
from agenteval.cost import parse_claude_code_output

REPO = Path(__file__).resolve().parent.parent
RUNS_DIR = REPO / "evals/runs"
os.environ["EVAL_DIR"] = str(REPO / "evals")
os.environ["EVAL_PYTEST"] = str(REPO / "python/.venv/bin/pytest")

# The repo's CLAUDE.md asks the agent to check in before working; nobody is there.
UNATTENDED = (
    "This is an unattended benchmark run. Do not wait for approval or ask "
    "questions: implement the change fully, then verify it."
)
ALLOWED_TOOLS = ["Bash(npm *)", "Bash(npx *)", "Bash(pytest *)", "Bash(python *)"]
BUDGET_USD = "3"


class ClaudeModelAdapter(AgentAdapter):
    model = ""

    def is_available(self) -> bool:
        return True

    async def run(self, task, workdir: str) -> dict:
        # Worktrees have no node_modules (gitignored); reuse the repo's.
        os.symlink(REPO / "node_modules", Path(workdir) / "node_modules")
        env = {**os.environ, "ECC_GATEGUARD": "off"}
        start = time.monotonic()
        proc = await asyncio.create_subprocess_exec(
            "claude", "-p", task.description,
            "--model", self.model,
            "--output-format", "json",
            "--permission-mode", "acceptEdits",
            "--allowedTools", *ALLOWED_TOOLS,
            "--max-budget-usd", BUDGET_USD,
            "--append-system-prompt", UNATTENDED,
            cwd=workdir, env=env,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        try:
            out, err = await asyncio.wait_for(proc.communicate(), task.timeout_seconds)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            out, err = b"", b"Timed out"
        self._save_diff(task, workdir)
        stdout = out.decode("utf-8", errors="replace")
        tokens, cost = parse_claude_code_output(stdout)
        if cost is None and out:
            # agent-eval doesn't know Claude Code's `total_cost_usd` field.
            data = json.loads(stdout)
            cost = data.get("total_cost_usd")
            tokens = tokens or sum(v for v in data.get("usage", {}).values() if isinstance(v, int))
        return {
            "exit_code": proc.returncode if out else -1,
            "stdout": stdout,
            "stderr": err.decode("utf-8", errors="replace"),
            "duration_seconds": time.monotonic() - start,
            "tokens_used": tokens,
            "cost_usd": cost,
        }

    def _save_diff(self, task, workdir: str) -> None:
        """Keep the agent's changes: agent-eval deletes the worktree after judging."""
        git = ["git", "-C", workdir]
        subprocess.run([*git, "add", "-A", "-N", "--", ".", ":!node_modules"], check=True)
        diff = subprocess.run([*git, "diff"], capture_output=True, text=True).stdout
        RUNS_DIR.mkdir(exist_ok=True)
        (RUNS_DIR / f"{task.id}-{self.name}-{time.strftime('%H%M%S')}.diff").write_text(diff)


class OpusAdapter(ClaudeModelAdapter):
    name = "opus"
    model = "claude-opus-5-5"


class SonnetAdapter(ClaudeModelAdapter):
    name = "sonnet"
    model = "claude-sonnet-5-5"


ADAPTERS.update({"opus": OpusAdapter, "sonnet": SonnetAdapter})

if __name__ == "__main__":
    cli.main()
