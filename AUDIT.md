# Dili Compliance QA — Audit

**Date:** 2026-10-18
**Scope:** `dili-qa-skeleton` (TypeScript + Playwright). Static review of the
compliance engine, scenario registry, tests, config, and CI, plus a live check
of the login flow at `BASE_URL`.
**Method:** code read + reproductions run in Node and Playwright. Each finding
below says whether it was *verified* here or still *needs confirmation*.

> The regulation citations in this file (Davis-Bacon, 29 CFR Part 5,
> 26 U.S.C. § 45(b)(8)) are real, but paragraph-level numbers should be
> re-checked against eCFR — the 2023 Davis-Bacon rule renumbered parts of
> 29 CFR 5.5. Rates and thresholds in the engine are illustrative, not legal
> advice.

---

## Summary

| # | Finding | Severity | Status |
|---|---------|----------|--------|
| 1 | Empty-string credentials returned `200` + a session token | Critical (security) | Verified live — escalate, do not publish details |
| 2 | Apprenticeship ratio: float error flags an exactly-at-threshold worker non-compliant | High (wrong verdict) | Verified in Node |
| 3 | Wage check reports a worker non-compliant with a `$0.00` shortfall | High (wrong verdict) | Verified in Node |
| 4 | CI triggers on `main`, but the only branch is `master` — CI never runs | High (process) | Verified |
| 5 | `.env.example` points at `https://www.houserx.com` | Medium | Verified |
| 6 | Empty login form submit gives no feedback (no validation) | Medium (UX) | Verified live; covered by `test.fail` |
| 7 | Tests run against the live production site by default | Medium (process) | Verified |
| 8 | Scenario coverage & citation gaps | Medium (structural) | Verified |
| 9 | Housekeeping: stray `.gitignore copy`, unpinned `@playwright/test: latest`, fixed `waitForTimeout` | Low | Verified |

---

## Critical

### 1. Empty-string credentials appear to authenticate
Sending the login API (`POST https://api.diliai.com/auth/login/`) a body of
`{"username":"","password":""}` returned **`200` with access + refresh JWTs**,
whereas unknown users, missing fields, and non-email usernames all return
`400 {"errors":{"login":"Invalid username or password"}}`.

This is a likely authentication bypass or a seed/test account with blank
credentials. **It is a security issue, not a normal QA bug.**

- Hand to Dili engineering/security to confirm against the backend.
- Do **not** paste the raw request/response or token into a public tracker or PR.
- The returned token was not used, reused, or probed further.
- No automated test is included for this yet — writing one requires confirming
  the intended behaviour first (empty login must be rejected).

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

---

## High — process

### 4. CI never runs on push
[`.github/workflows/ci.yml`](.github/workflows/ci.yml) triggers on
`push: branches: [main]`, but the repository's only branch is `master`
(`git branch` shows `master` / `origin/master`). Pushes therefore never trigger
CI; only pull requests would.

**Fix:** either rename the branch to `main`, or set the workflow to
`branches: [master, main]`.

---

## Medium

### 5. `.env.example` points at the wrong site
[`.env.example`](.env.example) sets `BASE_URL=https://www.houserx.com`, which
looks copied from another project. It should match this project
(`https://www.dili.com`).

### 6. Empty login form submit gives no feedback
Clicking **Sign in** with both fields blank fires no request and shows no
message — the inputs are not `required` and there is no client-side validation.
Captured as a `test.fail` test in
[`tests/login.spec.ts`](tests/login.spec.ts) so it is tracked and will flip to a
real pass once validation is added.

### 7. Tests run against production by default
`BASE_URL` defaults to the live Dili site, and the login specs
(including the invalid-credentials test that actually submits the form) run
against it. CI would hit production on every run.

**Fix:** point tests at a staging/preview environment, or mock the auth API, and
gate any live-site tests behind an explicit flag.

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

---

## Low — housekeeping

- Stray `.gitignore copy` file in the repo root; remove it.
- `@playwright/test` is pinned to `latest` in [`package.json`](package.json);
  pin an exact version for reproducible CI.
- The login specs use a fixed `waitForTimeout(1000)`; prefer waiting on a
  condition (response/locator) to avoid flake and wasted time.

---

## Suggested order of work

1. **Finding 1** — escalate the auth-bypass internally (today).
2. **Findings 2 & 3** — integer-cent / epsilon math; add property-based tests so
   the whole input range is covered, not three clean cases.
3. **Finding 4** — fix the CI branch trigger so the suite actually runs.
4. **Findings 5 & 7** — correct the example config; stop pointing tests at prod.
5. **Finding 8** — move scenario data into the registry, tighten citations and
   the meta-tests, add the missing test types.
6. **Finding 9** — housekeeping.
