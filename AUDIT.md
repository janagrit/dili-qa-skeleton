# Dili Compliance QA — Audit

**Date:** 2026-10-18
**Scope:** `dili-qa-skeleton` (TypeScript + Playwright). Static review of the
compliance engine, scenario registry, tests, config, and CI, plus a live check
of the login flow at `BASE_URL`.
**Method:** code read + reproductions run in Node and Playwright. Each finding
below says whether it was *verified* here or still *needs confirmation*.

> **Status (2026-10-19):** findings 2–5, 7 and 8 are fixed on `master`, and
> finding 9 is mostly fixed; see the *Status* column and the *Resolution* note
> under each finding. Findings 1 and 6 are in the live product and stay open.
>
> Citations are now paragraph-level and checked against eCFR / the U.S. Code:
> `29 CFR 5.5(a)(1)(i)` (wages and fringe), `29 CFR 5.5(a)(1)(iii)`
> (conformance), `26 U.S.C. 45(b)(8)(A)` (apprentice labor hours). Rates and
> thresholds in the engine are illustrative, not legal advice.

---

## Summary

| # | Finding | Severity | Status |
|---|---------|----------|--------|
| 1 | Login API security issue | Critical (security) | Open — shared with Dili; details withheld |
| 2 | Apprenticeship ratio: float error flags an exactly-at-threshold worker non-compliant | High (wrong verdict) | **Fixed** — regression test AP-003 |
| 3 | Wage check reports a worker non-compliant with a `$0.00` shortfall | High (wrong verdict) | **Fixed** — integer-cent math |
| 4 | CI triggers on `main`, but the only branch is `master` — CI never runs | High (process) | **Fixed** |
| 5 | `.env.example` points at `https://www.houserx.com` | Medium | **Fixed** |
| 6 | Empty login form submit gives no feedback (no validation) | Medium (UX) | Open (product) — tracked by `test.fail` |
| 7 | Tests run against the live production site by default | Medium (process) | **Fixed** — CI runs logic tests only |
| 8 | Scenario coverage & citation gaps | Medium (structural) | **Fixed** (Python suite); TS registry still has inputs in test code |
| 9 | Housekeeping: stray `.gitignore copy`, unpinned `@playwright/test: latest`, fixed `waitForTimeout` | Low | Mostly fixed — one `waitForTimeout` left |

---

## Critical

### 1. Login API security issue
A possible authentication weakness in the login API was found during the live
check. **It is a security issue, not a normal QA bug**, so the details are not
published in this public repository.

- Shared with Dili for confirmation against the backend.
- No token or session was used or probed further.
- A regression test will be added once the intended behaviour is confirmed.

---

## High — wrong compliance verdicts

These two bugs matter because the product's whole value is a correct
compliant / non-compliant decision. Both are floating-point errors; both are
invisible to the current tests because the tests use only clean inputs
(`15/100`, `10/100`, whole-dollar rates).

### 2. Apprenticeship ratio marks an at-threshold worker non-compliant
[`src/complianceEngine.ts:56-61`](src/complianceEngine.ts#L56-L61)

```
checkApprenticeshipRatio(0.3, 3, 0.10)
  → actualRatio (compared) = 0.09999999999999999  → compliant: false
  → actualRatio (displayed, round 4dp) = 0.1
```

`0.3 / 3` is exactly 10% but evaluates just under `0.10`, so the worker is
flagged non-compliant — while the *displayed* ratio rounds to `0.1`, i.e. the
report shows a number that meets the threshold next to a "non-compliant"
verdict. The comparison and the displayed value disagree.

**Fix:** compare on a rounded/epsilon basis, or use integer hour math, and make
the compared value and the displayed value the same.

**Resolution:** Python compares exact `Fraction`s; TypeScript compares hours
against `ratio × total` with a small tolerance. `0.3 / 3` at 10% is compliant
in both (scenario AP-003).

### 3. Wage check: non-compliant with a reported `$0.00` shortfall
[`src/complianceEngine.ts:32-38`](src/complianceEngine.ts#L32-L38)

```
required 45.00, paid 44.999
  → shortfall = 0.001           → compliant: false
  → shortfallPerHour (round 2dp) = 0.00
```

`compliant` is derived from the raw shortfall while `shortfallPerHour` is
rounded to cents, so a worker can be marked non-compliant with a `$0.00`
shortfall shown. Separately, the check compares **base pay only** — Davis-Bacon
requires base **plus fringe** (see Finding 8).

**Fix:** do the money math in integer cents and derive both the verdict and the
displayed shortfall from the same rounded number.

**Resolution:** both engines work in whole cents, and sub-cent amounts (e.g.
`44.995`) are rejected instead of rounded, so an underpayment can never round
up to a pass (TS PW-005, Python PW-006). The Python check also scores fringe.

---

## High — process

### 4. CI never runs on push
[`.github/workflows/ci.yml`](.github/workflows/ci.yml) triggers on
`push: branches: [main]`, but the repository's only branch is `master`
(`git branch` shows `master` / `origin/master`). Pushes therefore never trigger
CI; only pull requests would.

**Fix:** either rename the branch to `main`, or set the workflow to
`branches: [master, main]`.

**Resolution:** the workflow now triggers on `[master, main]` and also runs the
Python suite.

---

## Medium

### 5. `.env.example` points at the wrong site
[`.env.example`](.env.example) sets `BASE_URL=https://www.houserx.com`, which
looks copied from another project. It should match this project
(`https://www.dili.com`).

**Resolution:** `BASE_URL=` is now empty and falls back to the default.

### 6. Empty login form submit gives no feedback
Clicking **Sign in** with both fields blank fires no request and shows no
message — the inputs are not `required` and there is no client-side validation.
Captured as a `test.fail` test in
[`tests/login.spec.ts`](tests/login.spec.ts) so it is tracked and will flip to a
real pass once validation is added. *Still open in the product.*

### 7. Tests run against production by default
`BASE_URL` defaults to the live Dili site, and the login specs
(including the invalid-credentials test that actually submits the form) run
against it. CI would hit production on every run.

**Fix:** point tests at a staging/preview environment, or mock the auth API, and
gate any live-site tests behind an explicit flag.

**Resolution:** live-site specs (`login.spec.ts`, `site.spec.ts`) are in a
separate Playwright `ui` project run with `npm run test:ui`. `npm test`, which
CI runs, covers only the engine and registry. Python API tests are opt-in
(`DILI_RUN_API_TESTS=1`).

### 8. Coverage & citation gaps
- **Citations too broad.** Most prevailing-wage scenarios cite
  `29 CFR Part 5` rather than a specific paragraph (e.g. `29 CFR 5.5(a)(1)(i)`).
  A reviewer can't trace a verdict to the exact rule.
- **Wage model incomplete.** Base pay only; Davis-Bacon counts base + fringe.
- **Apprenticeship rules conflated.** One check mixes what are really distinct
  IRA requirements (ratio vs. labor-hours/participation).
- **No effective dates.** Thresholds change with the construction start date;
  the registry has no date dimension.
- **Scenario data lives in test code, not the registry.** Inputs and expected
  results are hard-coded in the `switch` blocks in
  [`tests/prevailing-wage.spec.ts`](tests/prevailing-wage.spec.ts) and
  [`tests/apprenticeship.spec.ts`](tests/apprenticeship.spec.ts), so a
  compliance reviewer can't read or add scenarios without editing code.
- **Registry meta-tests are shallow.** [`tests/registry.spec.ts`](tests/registry.spec.ts)
  only checks that fields are non-empty — not citation format, nor that every
  scenario has a matching test body.
- **Testing techniques absent.** No property-based, combinatorial, API,
  integration, or regression tests. The two verdict bugs above (2, 3) are
  exactly what property-based testing would catch.

**Resolution:** the Python suite (`python/`) keeps inputs and expected results
in the registry, uses paragraph-level citations checked against a reviewed
list, scores base + fringe, models the 10% / 12.5% / 15% apprentice
percentage by construction start date, rejects invalid input, and adds
property-based, combinatorial and opt-in API tests. The TypeScript registry
has the same citations and fixes, but its inputs still live in the spec files.

---

## Low — housekeeping

- Stray `.gitignore copy` file in the repo root; remove it.
- `@playwright/test` is pinned to `latest` in [`package.json`](package.json);
  pin an exact version for reproducible CI.
- The login specs use a fixed `waitForTimeout(1000)`; prefer waiting on a
  condition (response/locator) to avoid flake and wasted time.

**Resolution:** the stray file is removed and Playwright is pinned to `1.64.1`.
The one `waitForTimeout` in `login.spec.ts` remains.

---

## Still open

1. **Finding 1** — awaiting confirmation from Dili.
2. **Finding 6** — empty-login feedback; product fix needed. Tracked by `test.fail`.
3. **Finding 9** — replace the remaining `waitForTimeout` with a condition wait.
4. Move the TypeScript scenario inputs into the registry, as the Python suite does.

Live-site issues found after this audit (careers jobs feed returning 502,
`/landing/` serving XML, pages wider than a phone screen) are listed in the
README and tracked as known-bug tests in `tests/site.spec.ts`.
