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

---

# Run the UI tests with the browser visible

## Problem

`npm run test:ui` runs the live-site tests headless. `npm run test:headed` shows the
browser but has no `--project`, so it also runs the 13 logic tests, which don't use one.

## Todo

- [ ] 1. `package.json`: add `"test:ui:headed": "playwright test --project=ui --headed"`
- [ ] 2. `README.md`: add one line for it under `npm run test:ui`
- [ ] 3. Verify: `npx playwright test --project=ui --headed --list` lists the 19 UI tests
- [ ] 4. Review section

---

# Restructure the UI tests around a Page Object Model

## Problem

The UI specs drive pages directly: locators such as `getByRole('textbox', { name: 'Email' })`
are repeated across tests, and login helpers are plain functions inside `login.spec.ts`.
Logic and UI specs share one flat `tests/` folder, and the config tells them apart by file name.

## Target layout

```
tests/
  logic/      prevailing-wage, apprenticeship, registry .spec.ts   (moved, imports become ../../src)
  ui/         login.spec.ts, site.spec.ts                          (moved, rewritten to use pages)
  pages/      HomePage.ts, LoginPage.ts, SitePage.ts
  fixtures.ts test.extend({ homePage, loginPage, sitePage }) + re-export expect
```

Page objects hold locators and actions. Assertions stay in the specs (Playwright's
recommended style). Test titles, `test.fail` markers and behaviour stay exactly the same.

## Todo

- [x] 1. Save `npx playwright test --list` output as the "before" snapshot (13 logic + 19 UI)
- [x] 2. `git mv` the 3 logic specs to `tests/logic/` and fix their `../src` imports
- [x] 3. Add `tests/pages/HomePage.ts`: `goto()`, `openLogin()` (nav "Log In" link)
- [x] 4. Add `tests/pages/LoginPage.ts`: email/password/submit/forgot/SSO/error locators,
      `heading`, `signIn(email, password)`, `submitEmpty()`
- [x] 5. Add `tests/pages/SitePage.ts`: `goto(path)` returns the response, `footer`,
      `brokenImages()`, `renderedWidth()` (used by the BUG-3 checks)
- [x] 6. Add `tests/fixtures.ts` that provides the three pages to tests
- [x] 7. `git mv` the 2 UI specs to `tests/ui/` and rewrite them to use the fixtures.
      `/api/jobs` and `/landing/` checks keep using `request` (they are API checks, not pages)
- [x] 8. `playwright.config.ts`: projects use `testDir: './tests/logic'` and `'./tests/ui'`
      instead of the file-name globs
- [x] 9. Verify: `npm run typecheck`, `npm test` (13 pass), and `--list` matches the
      "before" snapshot apart from the new paths
- [x] 10. Review section

## Not in scope

- `waitForTimeout(1000)` in the empty-submit test stays as it is (behaviour change, separate task).
- `evals/` checks reference the old paths, but they run against the pinned commit `881aa6e`,
  so the move does not affect them.

## Review

- **Layout:** `tests/logic/` (3 compliance specs, moved, imports now `../../src`),
  `tests/ui/` (login + site specs), `tests/pages/` (page objects), `tests/fixtures.ts`.
- **Page objects:**
  - `HomePage`: nav "Log In" link; `openLogin()` returns the `LoginPage` once it has loaded.
  - `LoginPage`: form locators, error / validation messages, `signIn()`, `expectLoaded()`,
    `isLoginRequest()` (the login POST matcher), `url`.
  - `SitePage`: footer, `goto()`, `gotoAndSettle()`, `brokenImages()`, `renderedWidth()`,
    `recordServerErrors()`.
- **Fixtures:** `homePage`, `sitePage`. No `loginPage` fixture, because a `beforeEach` that opens
  login would also hit the live site for the valid-login test, which skips before navigating today.
- **Config:** projects pick tests by folder (`testDir`) instead of file-name globs. Project names unchanged.
- **Not changed:** test names, `test.fail` markers, assertions, the `waitForTimeout(1000)`, and the
  `/api/jobs` and `/landing/` request checks.
- **Verified:** `npm run typecheck` clean; `npm test` 13/13; `playwright test --list` gives the
  same 32 tests as before apart from the folder paths.
- **Not verified:** the 19 UI tests were not run against the live site.

---

# Shared JSON scenario data for the TypeScript and Python ports (after the POM work)

## Problem

Each scenario is defined twice. Python keeps the inputs and the expected verdict in
`python/dili_compliance/registry.py`; TypeScript keeps only id/rule/citation in
`src/scenarioRegistry.ts` and types the inputs into a `switch` in each spec. The two
copies drift: same ID, different inputs (e.g. PW-001 is 45.00 + 12.50 fringe in Python,
45.00 base only in TS).

## Blocker

The TS engine does not score fringe yet. Python's wage scenarios use fringe, so the two
ports can only share wage inputs once TS supports it (the `ts-fringe-support` eval task;
Sonnet's or Opus's diffs from `evals/runs/` are a starting point). Apprenticeship
scenarios have no fringe and can be shared straight away.

## Todo

- [ ] 1. Decide: add fringe to the TS engine first, or share AP-* only for now
- [ ] 2. Add `scenarios/scenarios.json` (tsconfig already includes `scenarios/`):
      id, area, rule, citation, description, tags, `input`, `expect`.
      Money and ratios as strings (`"45.00"`, `"0.15"`) so Python keeps exact `Decimal`.
      `expect` is `{ "compliant": bool }` or `{ "error": "KeyError" | "ValueError" }`
- [ ] 3. Python: `registry.py` builds `SCENARIO_REGISTRY` from the JSON into the existing
      dataclasses, so `runner.py` and the tests don't change. `RATES`, `CITATIONS` stay in code
- [ ] 4. TS: `scenarioRegistry.ts` reads the JSON; each spec loops over it, calls the engine
      with `input` and checks `expect`. The `switch` blocks go away.
      `error` means "throws" in TS (TS errors are plain `Error`, not KeyError/ValueError)
- [ ] 5. Keep extra TS-only checks that the JSON can't express (PW-002 shortfall = 5.00,
      PW-006 44.99 -> shortfall 0.01) as separate named tests
- [ ] 6. Registry meta-tests (TS `registry.spec.ts`, Python `test_registry.py`) run on the
      JSON; the cross-port ID test becomes unnecessary (one file = one set of IDs)
- [ ] 7. Verify: `npm run typecheck`, `npm test`, `cd python && pytest -q`; test count and
      names unchanged apart from intended additions
- [ ] 8. Review section

---

# Make the eval checkers work on the new test layout

## Problem

`evals/checks/*.sh` use the old flat paths (`tests/login.spec.ts`, `tests/prevailing-wage.spec.ts`,
and copy the hidden fringe spec into `tests/`, which is now in neither project). The suite still
runs them against `881aa6e` (old layout), so they must keep working there too. Run by hand in the
repo, they also leave changes behind (PW-099 rename, copied hidden spec).

## Todo

- [x] 1. `login-no-wait.sh`: use `tests/ui/login.spec.ts`, fall back to `tests/login.spec.ts`
- [x] 2. `cross-port-ids.sh`: use `tests/logic/prevailing-wage.spec.ts` (fallback to old path);
      back up the two renamed files and restore them on exit
- [x] 3. `ts-fringe.sh`: copy the hidden spec into `tests/logic/` with a `../../src` import
      when that folder exists (else `tests/` as before); remove the copy on exit
- [x] 4. `evals/README.md`: how to run a checker by hand
- [x] 5. Verify on the current code: each checker fails (baseline) and leaves `git status` unchanged;
      login checker passes with a `networkidle` fix in a scratch copy
- [x] 6. Review section

## Review

- **Paths:** each judge tries the new path (`tests/ui/`, `tests/logic/`) and falls back to the
  old flat `tests/`, so the eval suite pinned to `881aa6e` still works.
- **Hidden fringe spec:** copied into `tests/logic/` with its import rewritten to `../../src`.
  Before this, on the new layout it would have landed in `tests/`, outside both projects, and
  never run.
- **Cleanup:** `cross-port-ids.sh` backs up and restores the two files it renames;
  `ts-fringe.sh` deletes the copied hidden spec. Both use `trap ... EXIT`, so cleanup also
  happens when the judge fails.
- **README:** `evals/README.md` shows how to run a judge by hand.
- **Verified:** on the current code all three judges fail for the expected reason (sleep still
  there / no `fringeRate` / PW-099 not caught) and `git status` is unchanged afterwards. In a
  scratch copy with a `networkidle` fix, `login-no-wait.sh` passes. That also ran the new
  `HomePage` -> `LoginPage` page objects in a real browser against the mock login page.
- **Not verified:** a passing run of `ts-fringe.sh` or `cross-port-ids.sh` (that needs the
  solutions, which are your exercises 7 and 8).

---

# Live-site findings update (2026-10-23)

- [x] 1. BUG-2 (`/landing/`): confirmed still open. It is Hugo's RSS feed for the landing-page
      section; nothing on the 6 main pages links to it, but `sitemap.xml` lists it.
      `FINDINGS.md` #3 updated with this, severity Medium -> Low.
- [x] 2. BUG-1 (`/api/jobs`): fixed in production (200 with the job list, careers page has no 5xx).
      The two tests lost `.fail` and moved from `known production bugs` to `site health` as
      regression guards (same titles). `FINDINGS.md` #2, status line and the
      "How to reproduce" note updated.

## Review

- **Verified:** `npm run typecheck` clean; both BUG-1 tests pass against the live site; still
  19 UI tests; BUG-2 still reports as Known bug.
- **Not checked today:** BUG-3 (mobile width) and BUG-4 (empty login form).
- **Left as is:** `FINDINGS.md` line 11 says a fixed bug's test "passes"; with `test.fail` it
  is reported as failed ("expected to fail, but passed"), as "How to reproduce" says.
