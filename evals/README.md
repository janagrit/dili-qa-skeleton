# Agent evals

Opus vs Sonnet (both via Claude Code) on three real open items from
`tasks/todo.md`, pinned to commit `881aa6e`. Uses
[agent-eval](https://github.com/joaquinhuigomez/agent-eval) plus the local
adapters in `run.py`.

| Task                  | Judge (`checks/`)                                                    |
|-----------------------|----------------------------------------------------------------------|
| `ts-fringe-support`   | hidden fringe spec + `npm run typecheck` + `npm test`                |
| `login-no-fixed-wait` | no `waitForTimeout` + typecheck; the test runs against `mock-login-server.js`: it must pass when the page sends nothing and fail when it POSTs at once or 250ms later |
| `cross-port-id-check` | both suites pass, then must fail after a TS-only ID rename (PW-099)  |

Every judge fails on the baseline commit, so an agent that does nothing scores 0.
Each run's `git diff` is saved to `evals/runs/` (gitignored), so failed runs can be inspected.

## Run

Needs Python 3.10+, `node_modules`, and `python/.venv` (the worktrees reuse them).

```sh
python3.12 -m venv .eval-venv && .eval-venv/bin/pip install <path-to-agent-eval-checkout>
.eval-venv/bin/python evals/run.py run --tasks evals/suite.yaml --agents opus,sonnet --runs 3 --output evals/report.json
git worktree prune   # git < 2.17 can't remove agent-eval's worktrees itself
```

Each agent run is capped at $3 (`--max-budget-usd`). GateGuard is turned off
inside agent runs only (`ECC_GATEGUARD=off`).

## Results

Run 2026-10-22, 3 runs per task, total spend $8.07 (`report.json`).

| Agent  | Pass rate | Avg time | Avg cost | Consistency |
|--------|-----------|----------|----------|-------------|
| opus   | 6/9 (67%) | 94.5s    | $0.67    | 0.53        |
| sonnet | 9/9 (100%)| 52.5s    | $0.23    | 1.00        |

| Task                  | opus | sonnet |
|-----------------------|------|--------|
| `ts-fringe-support`   | 3/3  | 3/3    |
| `cross-port-id-check` | 3/3  | 3/3    |
| `login-no-fixed-wait` | 0/3  | 3/3    |

The first judge for `login-no-fixed-wait` grepped for the variable name `loginAttempted`,
so it failed Opus for renaming it. It is now behavioural (mock login page, see above).
Rerun of that task with the new judge, $1.74 (`report-login-v2.json`, diffs in `runs/`):

| Agent  | `login-no-fixed-wait` (v2 judge) | Wait strategy used                                  |
|--------|----------------------------------|-----------------------------------------------------|
| opus   | 0/3                              | `setTimeout(0)` barrier, sentinel request ×2         |
| sonnet | 2/3                              | `networkidle` ×2 (pass), double `requestAnimationFrame` (fail) |

Every failure was the same miss: a login POST sent 250ms after the click.
Event-loop barriers and sentinel requests only catch a POST sent synchronously in the
click handler. `networkidle` waits for about 500ms of network quiet, so it catches the late one.

**Overall (with v2 login judge):** opus 6/9, sonnet 8/9. Sonnet was about 2× faster
and 3× cheaper on every task.
