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
