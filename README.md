# QA skeleton: executable compliance scenario registry

Interview-prep skeleton for a **Senior QA Engineer** role at a compliance-tech
startup (think Dili-style: prevailing wage + apprenticeship compliance).
Playwright + TypeScript. Small on purpose: open it, run it, extend it.

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
  tests (`login.spec.ts`) are never run in CI.
- `python/` — the Python reference implementation and fuller suite
  (fringe benefits, input validation, effective dates, property-based,
  combinatorial and opt-in API tests). See `python/README.md`.

This mirrors the 90-day plan from the posting: scenario registry with
citations, CI-gated releases, every defect becomes a permanent regression
test.

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
| `cd python && pytest` (CI) | 57 (+4 opt-in API) | Python engine: scenarios, citations, validation, effective dates, property-based, combinatorial | No (API tests opt-in) |
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

## Extend it (good next steps for tomorrow)

1. Add a scenario to `scenarioRegistry.ts` (e.g. overtime, certified payroll)
   and watch the meta-test force you to give it a citation.
2. Add the test body in the matching spec file.
3. Turn a bug you find into a permanent regression scenario with its citation.

## Honesty notes

- Regulation citations (Davis-Bacon Act, 29 CFR Part 5, 26 U.S.C. § 45(b)(8))
  are real. Rates, thresholds and engine logic are **illustrative examples**,
  not legal advice and not any company's real implementation.
