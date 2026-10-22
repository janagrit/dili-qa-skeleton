# Align scenario IDs between the TypeScript and Python registries

## Problem

The same scenario ID means different rules in the two ports, which breaks the
"scenario id -> rule -> citation" traceability the registries exist for.

| ID     | TypeScript (`src/scenarioRegistry.ts`) | Python (`python/dili_compliance/registry.py`) |
|--------|----------------------------------------|-----------------------------------------------|
| PW-003 | paid above the rate -> compliant       | fringe shortfall covered by extra base pay    |
| PW-004 | unknown classification -> throws       | base shortfall not curable by fringe          |
| PW-005 | sub-cent rate ($44.995) -> rejected    | unknown classification -> raises              |
| PW-006 | —                                      | sub-cent rate ($44.995) -> rejected           |
| AP-004 | apprentice > total AND negative hours  | apprentice > total only                       |
| AP-005 | —                                      | negative hours -> rejected                    |

PW-001, PW-002, AP-001, AP-002 and AP-003 already match.

## Approach

Python is the reference implementation, and `python/README.md` already cites
its IDs, so **Python IDs stay as they are and TypeScript is renumbered to match**.
Rule: one ID means one rule in both ports. TS may cover only a subset (it has no
fringe), so gaps in TS numbering are fine.

## Todo

- [x] 1. `src/scenarioRegistry.ts`: rename TS `PW-004` (unknown classification) -> `PW-005`
- [x] 2. `src/scenarioRegistry.ts`: rename TS `PW-005` (sub-cent) -> `PW-006`
- [x] 3. TS "paid above the rate" has no Python equivalent: give it new ID `PW-008`,
      and add a matching Python `PW-008` scenario (base + fringe above the
      required total is compliant), which is one registry entry and no test code
- [x] 4. Split the negative-hours check out of TS `AP-004` into a new TS `AP-005`
      (matches Python `AP-005`)
- [x] 5. Update the `case` labels in `tests/prevailing-wage.spec.ts` and
      `tests/apprenticeship.spec.ts` to the new IDs
- [x] 6. Add a one-line comment at the top of both registries: "IDs are shared
      with the other port; one ID = one rule"
- [x] 7. Verify: `npm run typecheck`, `npm test`, `cd python && pytest -q`
- [x] 8. Add a review section below

## Out of scope (not doing unless you ask)

- An automated cross-language check that the IDs stay in sync (would need one
  side to parse the other's source, which is fragile)
- The other review items: TS ignoring fringe, moving TS inputs into the registry,
  the fixed `waitForTimeout` in the login test

## Review

**Result:** every scenario ID now means the same rule in both ports.

| Rule                                   | Before (TS) | After (TS & Python) |
|----------------------------------------|-------------|---------------------|
| Unknown classification fails loudly    | PW-004      | PW-005              |
| Sub-cent rate is rejected              | PW-005      | PW-006              |
| Paid above the rate is compliant       | PW-003      | PW-008 (new in Python too) |
| Negative apprentice hours are rejected | inside AP-004 | AP-005 (own scenario) |

**Files changed**
- `src/scenarioRegistry.ts`: renumbered 3 IDs, added AP-005, header note on shared IDs
- `tests/prevailing-wage.spec.ts`: `case` labels renamed; assertions unchanged
- `tests/apprenticeship.spec.ts`: negative-hours assertion moved from AP-004 to AP-005
- `python/dili_compliance/registry.py`: added PW-008 (data only), header note on shared IDs

**Verification**
- `npm run typecheck`: clean
- `npm test`: 13 passed (was 12; +AP-005)
- `pytest -q`: 58 passed, 3 skipped (opt-in live API tests); scenario table shows 13/13

**Notes**
- No engine logic changed; only test IDs/labels and one new data scenario per port.
- Python PW-003/PW-004 (fringe rules) have no TS equivalent, so TS skips those
  numbers and PW-007 by design.
- Drift is still only prevented by convention (header comments). An automated
  cross-port check stays out of scope.

---

# Set up an agent-eval benchmark for this repo

## Problem

We want measured pass rate, cost and time for coding agents on this repo's real
work, not impressions. `/ecc:agent-eval` gives a YAML task format plus a CLI
(`agent-eval`) that runs each agent in its own git worktree and judges the result.

## Constraints found

- `agent-eval`, `aider` and `codex` are not installed. Only Claude Code is available.
- `agent-eval` is a third-party tool (github.com/joaquinhuigomez/agent-eval). Its
  source must be reviewed before we install it.
- Task YAMLs must pin a commit, but the ID-alignment work above is staged and not
  committed yet. It needs a commit before it can be pinned.
- `tasks/` already holds this todo file, so the eval YAMLs go in `evals/` instead.

## Todo

- [x] 1. Commit the staged ID-alignment work, then use that SHA as the pinned commit
      (done: `881aa6e` on new branch `agent-eval`)
- [x] 2. Review the agent-eval source (install method, what it runs, how it gets API keys),
      then install it only if it looks safe (done: installed in a scratchpad venv, Python 3.12)

## Source review findings (step 2)

- Safe: deps are only `pydantic` + `pyyaml`; it shells out to `git worktree`, the agent CLI,
  and our own `test_cmd`. No telemetry, no key handling (agents use their own auth).
- The skill doc's YAML format is wrong. Real format: one suite file with
  `name` + `tasks: [{id, description, repo, ref, test_cmd, timeout_seconds}]`.
  One `test_cmd` string per task (chain checks with `&&`). No grep/LLM judge types.
- Adapters: `claude-code`, `aider`, `mock` only. No Codex, and no way to choose a model.
- `claude-code` runs `claude -p "<task>"` with no permission flags, so in headless mode
  edits may be denied and the run does nothing.
- Worktrees have no `node_modules`, so each `test_cmd` must start with `npm ci`.
- Each judge must FAIL at `881aa6e`, or an agent that does nothing still "passes".
  So tasks need a check the baseline doesn't already meet.
- [x] 3. Write 3 task YAMLs in `evals/`, using the open items above as real tasks:
  - `ts-fringe-support.yaml`: the TS engine counts fringe like the Python port does.
    Judge: `npm run typecheck` + `npm test`
  - `login-no-fixed-wait.yaml`: replace `waitForTimeout` in `tests/login.spec.ts`.
    Judge: grep finds no `waitForTimeout` + `npm run typecheck`
  - `cross-port-id-check.yaml`: add a test that the TS and Python scenario IDs match.
    Judge: `cd python && pytest -q` + `npm test`
- [x] 3b. Add `evals/run.py`: local Opus/Sonnet adapters (model + edit permission + $3 cap)
- [x] 3c. Check every judge FAILS on the baseline commit (all 3 do)
- [x] 4. Add `evals/README.md` with the run command and results table (a few lines)
- [x] 5. Smoke-run 1 task × 1 agent × 1 run to check the judges work
      (sonnet / login-no-fixed-wait: PASS, 18.5s, $0.16, 5 turns, 0 permission denials.
      Fixed: agent-eval didn't read Claude's `total_cost_usd`, so the adapter does now)
- [x] 6. Full run: chosen agents × 3 tasks × 3 runs; record the report table (in `evals/README.md`)
- [x] 7. Add a review section below

## Review

**Result:** Opus vs Sonnet (via Claude Code), 3 real tasks × 3 runs, $8.07 total.

| Agent  | Pass rate | Avg time | Avg cost |
|--------|-----------|----------|----------|
| opus   | 6/9       | 94.5s    | $0.67    |
| sonnet | 9/9       | 52.5s    | $0.23    |

- Both models pass 3/3 on `ts-fringe-support` and `cross-port-id-check`, which have
  behavioural judges. Sonnet is about 2× faster and 3× cheaper there.
- The 0/3 for Opus on `login-no-fixed-wait` is a judge artifact. Opus wrote stronger
  fixes but renamed `loginAttempted`, which the judge greps for by name. Sonnet passed
  3/3 with a weaker `networkidle` wait.

**Files added**
- `evals/suite.yaml`: 3 tasks pinned to `881aa6e`
- `evals/checks/*.sh`, `evals/checks/fringe.hidden.spec.ts`: judges. All 3 fail on the baseline.
- `evals/run.py`: Opus/Sonnet adapters (model, edit permission, $3 cap, cost parsing)
- `evals/README.md`: how to run, the judges, results
- `evals/report.json`: the raw report

**Other changes**
- Committed the ID-alignment work as `881aa6e` on new branch `agent-eval`. Nothing pushed.
- agent-eval is installed only in a scratchpad venv, not in the project.

**Notes / follow-ups (not done)**
- Fix the login judge so it checks behaviour, not a variable name. For example, run the
  spec against a mocked `/login` page that does or doesn't POST. Then rerun that task.
- agent-eval deletes worktrees, so failed runs can't be diffed afterwards. Saving
  `git diff` in the adapter would help.
- Git 2.15 can't run `git worktree remove`, so run `git worktree prune` after each eval.

---

# Follow-ups to the agent eval

- [x] 1. Make the login judge test behaviour instead of a variable name. Run the agent's
      "does not sign the user in" test against a local mock login page in 3 modes:
      `good` (empty submit sends nothing) must PASS; `bad-now` (empty submit POSTs at once)
      and `bad-late` (POSTs after 250ms, still inside the old 1s guarantee) must FAIL.
      Keep the "no `waitForTimeout`" check. Validate it on the baseline test and on Sonnet's `networkidle` fix.
      (Validated: 1s sleep and `networkidle` both PASS/FAIL/FAIL, failing on the login-API assertion.
      A sentinel-request fix misses the 250ms POST.)
- [x] 2. Adapter saves each run's `git diff` to `evals/runs/` (gitignored) before the worktree is deleted
- [x] 3. Rerun `login-no-fixed-wait` only: opus + sonnet × 3 (~$2.5); update README results
      (cost $1.74: opus 0/3, sonnet 2/3. Replayed every saved diff through the judge, and each verdict reproduced)
- [x] 4. Commit `evals/` + `tasks/todo.md` on branch `agent-eval` (no push)

## Review (follow-ups)

- **Login judge:** now behavioural. The agent's test runs against `evals/checks/mock-login-server.js`
  in 3 modes. It no longer greps for a variable name.
- **Diffs:** the adapter saves each run's diff to `evals/runs/` (gitignored), so failures can be inspected and replayed.
- **Rerun:** opus 0/3, sonnet 2/3. Every failure missed a POST sent 250ms late. Fixes that wait one
  event-loop tick, an animation frame or a sentinel request miss it. `networkidle` catches it.
  The first "judge artifact" explanation was half right: the old judge did fail Opus unfairly,
  but Opus's fixes also had a real gap.
- **Overall:** opus 6/9, sonnet 8/9. Total eval spend $9.81 ($8.07 + $1.74).
- **Open question (not done):** is 250ms the right bar? The task said "keep the guarantee",
  and the old 1s sleep met it, so I held fixes to that standard.
