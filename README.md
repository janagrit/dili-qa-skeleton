# Dili compliance QA: executable scenario registry

A compliance-testing project for prevailing-wage and apprenticeship rules
(Dili-style). Playwright + TypeScript, with a Python reference implementation.
Small and self-contained: open it, run it, extend it.

## The idea

The test suite is an **executable specification of the compliance engine**:

- `src/scenarioRegistry.ts` — every rule from the source regulation becomes a
  cited, deterministic test scenario (scenario id -> rule -> citation).
- `src/complianceEngine.ts` — a tiny illustrative stub of the engine under
  test. Replace with the real engine or API calls.
- `tests/` — one test per scenario, generated from the registry, plus
  `registry.spec.ts`: meta-tests proving every scenario has a citation
  (audit traceability).
- `.github/workflows/ci.yml` — CI-gated releases: typecheck + logic tests
  (TypeScript) and the Python suite on every push and PR. The live-site UI
  tests (`login.spec.ts`, `site.spec.ts`) are never run in CI.
- `python/` — the Python reference implementation and fuller suite
  (fringe benefits, input validation, effective dates, property-based,
  combinatorial and opt-in API tests). See `python/README.md`.

The approach: a scenario registry with citations, CI-gated releases, and every
defect captured as a permanent regression test.

## Run it

```bash
npm install
npm test            # engine + registry tests (no browser, no network) — what CI runs
npm run typecheck   # tsc --noEmit

# UI tests drive the live site; run them deliberately:
npx playwright install chromium
npm run test:ui
```

## What "green" means

| Suite | Tests | What it checks | Touches dili.com? |
|---|---|---|---|
| `npm test` (CI) | 12 | Illustrative compliance engine + scenario registry (TypeScript) | No |
| `cd python && pytest` (CI) | 57 (+3 opt-in API) | Python engine: scenarios, citations, validation, effective dates, property-based, combinatorial | No (API tests opt-in) |
| `npm run test:ui` | 19 | Live site: login flow, page health, known production bugs | **Yes** |

A green CI run means the **compliance logic and registry** are correct. It says
nothing about the live website: those tests are deliberately kept out of CI.

Known production bugs are written as `test.fail(...)` in `tests/site.spec.ts`
and `tests/login.spec.ts`. Each asserts the correct behaviour and is *expected*
to fail, so the run stays green while the report lists the bug; when Dili fixes
it, the test fails ("expected to fail, but passed") and the marker is removed.

| Bug | Test |
|---|---|
| BUG-1 `/api/jobs` returns 502 "Dover API error"; careers page lists no jobs | `site.spec.ts` |
| BUG-2 `/landing/` serves raw XML instead of HTML | `site.spec.ts` |
| BUG-3 `/`, `/privacy/`, `/landing/ira-landing/` are wider than a 390px phone | `site.spec.ts` |
| BUG-4 Empty login form gives no validation message | `login.spec.ts` |

Full write-up with expected behaviour for each: [`AUDIT.md`](AUDIT.md).

### Example `npm run test:ui` output

Every Playwright run ends with a summary table (custom reporter in
`reporters/table-summary-reporter.js`). It marks the known-bug `test.fail` tests
as **Known bug** — expected failures, kept separate from genuine `Failed` — so
the run stays green (exit 0). The last `npm run test:ui` run:

```
┌───────────────────────┬────────────────────────────────────────────────────┬───────────┬──────────┐
│ Test Suite            │ Test Name                                          │ Status    │ Duration │
├───────────────────────┼────────────────────────────────────────────────────┼───────────┼──────────┤
│ login                 │ home page "Log In" opens the sign-in form          │ Passed    │ 2s       │
│ login                 │ valid credentials sign the user in                 │ Skipped   │ 0s       │
│ login                 │ invalid credentials show error and stay on sign-in │ Passed    │ 3s       │
│ login                 │ empty form submit does not sign the user in        │ Passed    │ 3s       │
│ login                 │ empty form submit shows a validation message       │ Known bug │ 13s      │
│ site health           │ / loads with a title and footer                    │ Passed    │ 1s       │
│ site health           │ /careers/ loads with a title and footer            │ Passed    │ 1s       │
│ site health           │ /case-studies/ loads with a title and footer       │ Passed    │ 1s       │
│ site health           │ /terms/ loads with a title and footer              │ Passed    │ 1s       │
│ site health           │ /privacy/ loads with a title and footer            │ Passed    │ 1s       │
│ site health           │ /about/ loads with a title and footer              │ Passed    │ 2s       │
│ site health           │ home page has no broken images                     │ Passed    │ 2s       │
│ known production bugs │ BUG-1: /api/jobs returns job listings              │ Known bug │ 0s       │
│ known production bugs │ BUG-1: careers page shows no server errors on load │ Known bug │ 2s       │
│ known production bugs │ BUG-2: /landing/ serves an HTML page               │ Known bug │ 0s       │
│ mobile layout         │ BUG-3: / fits a 390px phone screen                 │ Known bug │ 2s       │
│ mobile layout         │ BUG-3: /privacy/ fits a 390px phone screen         │ Known bug │ 2s       │
│ mobile layout         │ BUG-3: /landing/ira-landing/ fits a 390px phone    │ Known bug │ 1s       │
│ mobile layout         │ /about/ fits a 390px phone screen (control)        │ Passed    │ 3s       │
└───────────────────────┴────────────────────────────────────────────────────┴───────────┴──────────┘

Total: 19
Passed: 11
Failed: 0
Known bugs (expected fail): 7
Skipped: 1
```

The 7 **Known bug** rows are the `test.fail` tests above (BUG-1 ×2, BUG-2,
BUG-3 ×3, BUG-4): expected failures, so `npm run test:ui` exits 0. If Dili fixes
a bug, that test passes unexpectedly and the reporter flips it to **Failed** —
the signal to remove the marker. The 1 skip is the valid-login test, which needs
`DILI_EMAIL` / `DILI_PASSWORD`.

## Extend it (good next steps)

1. Add a scenario to `scenarioRegistry.ts` (e.g. overtime, certified payroll)
   and watch the meta-test force you to give it a citation.
2. Add the test body in the matching spec file.
3. Turn a bug you find into a permanent regression scenario with its citation.

## Honesty notes

- Regulation citations (Davis-Bacon Act, 29 CFR Part 5, 26 U.S.C. § 45(b)(8))
  are real. Rates, thresholds and engine logic are **illustrative examples**,
  not legal advice and not any company's real implementation.
