# Python compliance suite

A Python reference implementation of the compliance engine and scenario
registry. It uses exact money and ratio math and adds broader testing techniques (property-based,
combinatorial, and opt-in API tests).

## What's here

| Path | Purpose |
|------|---------|
| `dili_compliance/engine.py` | Engine: integer-cent money (`Decimal`), exact `Fraction` ratios, Davis-Bacon base **+ fringe** |
| `dili_compliance/registry.py` | Scenarios with **paragraph-level** citations; inputs + expected verdicts live in the registry, not test code |
| `tests/test_registry.py` | Meta-tests: unique ids, present fields, and citation *format* (no bare "Part 5") |
| `tests/test_scenarios.py` | One test per registry scenario (unit) |
| `tests/test_property_based.py` | **Property-based** (Hypothesis) invariants across the whole input range |
| `tests/test_combinatorial.py` | **Combinatorial** cross-product of base/fringe pay positions |
| `tests/test_validation_and_dates.py` | Invalid-input rejection (sub-cent, negative, NaN, apprentice > total) and effective-date boundaries |
| `tests/test_api_login.py` | **API** tests for the login endpoint (opt-in; off by default) |
| `dili_compliance/runner.py` | Runs a registry scenario and captures the verdict or the expected error |

## Highlights

- **Paragraph-level, reviewed citations** — `29 CFR 5.5(a)(1)(i)` (wages + fringe),
  `29 CFR 5.5(a)(1)(iii)` (conformance), `26 U.S.C. 45(b)(8)(A)` (apprentice labor
  hours). Every citation must be on the `CITATIONS` list in the registry, so a
  well-formed but wrong paragraph fails the meta-tests.
- **Input validation** — sub-cent money is rejected, not rounded ($44.995 no longer
  passes as $45.00); negative / NaN values and apprentice hours above total are
  rejected (PW-006, PW-007, AP-004, AP-005).
- **Effective dates** — `applicable_percentage()` returns 10% / 12.5% / 15% by
  construction start date (26 U.S.C. 45(b)(8)(A)(ii)), tested at each boundary.
- **Fringe benefits** — the wage check scores base + fringe, with base-rate and
  total-compensation rules.
- **Property-based / combinatorial / API testing** — all three present; the
  property tests check verdicts across the whole input range, not just clean values.
- **Exact math** — no non-compliant-with-$0.00-shortfall; exactly-at-
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
Each run ends with a compliance scenario table (scenario, citation, expected
result, PASS/FAIL), printed by `tests/conftest.py`, so every run leaves a
readable record of what was tested.

> Rates, thresholds, and engine logic are illustrative, not legal advice and not
> Dili's real implementation.
