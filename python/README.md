# Python compliance suite

A Python port of the compliance engine and scenario registry, added to address
the audit (`../AUDIT.md`) and the job description's Python requirement. It fixes
the two verdict bugs from the TypeScript version and adds the testing techniques
the JD lists.

## What's here

| Path | Purpose |
|------|---------|
| `dili_compliance/engine.py` | Engine: integer-cent money (`Decimal`), exact `Fraction` ratios, Davis-Bacon base **+ fringe** |
| `dili_compliance/registry.py` | Scenarios with **paragraph-level** citations; inputs + expected verdicts live in the registry, not test code |
| `tests/test_registry.py` | Meta-tests: unique ids, present fields, and citation *format* (no bare "Part 5") |
| `tests/test_scenarios.py` | One test per registry scenario (unit) |
| `tests/test_property_based.py` | **Property-based** (Hypothesis) invariants across the whole input range |
| `tests/test_combinatorial.py` | **Combinatorial** cross-product of base/fringe pay positions |
| `tests/test_api_login.py` | **API** tests for the login endpoint (opt-in; off by default) |

## Audit items addressed

- **Python, not just TypeScript** — full parallel engine + suite.
- **Paragraph-level citations** — e.g. `29 CFR 5.5(a)(1)(i)`, `26 U.S.C. 45(b)(8)(B)`
  (re-verify against eCFR; the 2023 DBA rule renumbered parts of 5.5).
- **Fringe benefits** — the wage check scores base + fringe, with base-rate and
  total-compensation rules.
- **Property-based / combinatorial / API testing** — all three present; the
  property tests are what catch the float bugs the example-based tests missed.
- **Verdict bugs fixed** — no non-compliant-with-$0.00-shortfall; exactly-at-
  threshold ratios (0.3/3 == 10%) are compliant.

## Run it

```bash
cd python
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-test.txt
pytest -q                      # unit + property + combinatorial (API skipped)
pytest -m property             # just the Hypothesis tests
DILI_RUN_API_TESTS=1 pytest -m api   # opt in to live API tests (hits production)
```

API tests are skipped unless `DILI_RUN_API_TESTS=1` so CI never hits production.
`test_empty_string_credentials_are_rejected` is an `xfail` tracking audit
finding #1 (empty-string login returned a token) — it documents the intended
behaviour without failing the build, and will flip to a real pass once the
backend rejects empty credentials.

> Rates, thresholds, and engine logic are illustrative, not legal advice and not
> Dili's real implementation.
