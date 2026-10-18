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
- `.github/workflows/ci.yml` — CI-gated releases: typecheck + tests on
  every push and PR.

This mirrors the 90-day plan from the posting: scenario registry with
citations, CI-gated releases, every defect becomes a permanent regression
test.

## Run it

```bash
npm install
npx playwright install chromium
npm test          # run the suite
npm run typecheck # tsc --noEmit
```

## Extend it (good next steps for tomorrow)

1. Add a scenario to `scenarioRegistry.ts` (e.g. overtime, certified payroll)
   and watch the meta-test force you to give it a citation.
2. Add the test body in the matching spec file.
3. Turn a bug you find into a permanent regression scenario with its citation.

## Honesty notes

- Regulation citations (Davis-Bacon Act, 29 CFR Part 5, 26 U.S.C. § 45(b)(8))
  are real. Rates, thresholds and engine logic are **illustrative examples**,
  not legal advice and not any company's real implementation.
