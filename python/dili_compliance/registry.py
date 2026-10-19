"""Scenario registry: the executable specification of the compliance engine.

Every rule becomes a cited, deterministic scenario an auditor can trace:
scenario id -> rule -> paragraph-level citation -> inputs -> expected result.

Unlike the TypeScript version, the inputs and the expected verdict live here in
the registry (not hard-coded in test bodies), so a compliance reviewer can read
and add scenarios without touching test code. Citations are paragraph-level
(e.g. ``29 CFR 5.5(a)(1)(i)``), not just ``29 CFR Part 5``.

Re-verify citations against eCFR / uscode.house.gov when a rule changes: the 2023
Davis-Bacon final rule renumbered parts of 29 CFR 5.5.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal, Optional

Area = Literal["prevailing-wage", "apprenticeship"]

# Illustrative wage determination (base, fringe) by classification.
RATES = {
    "Electrician": ("45.00", "12.50"),
    "Laborer": ("28.50", "9.00"),
}

# Illustrative applicable percentage. Under 26 U.S.C. 45(b)(8)(A)(ii) it is 10%
# (construction begins before 2023), 12.5% (begins in 2023) or 15% (begins after
# 2023); see ``engine.applicable_percentage``.
REQUIRED_RATIO = "0.15"

ErrorName = Literal["KeyError", "ValueError"]

# Citations a scenario may use, with the heading of the cited provision. A
# scenario citing anything not listed here fails the registry meta-tests, so a
# well-formed but wrong paragraph (e.g. 45(b)(8)(B) for a labor-hours test)
# has to be added here deliberately, where a reviewer can check the heading.
# Headings checked against eCFR and 26 U.S.C. 45 on 2026-10-18.
CITATIONS = {
    "29 CFR 5.5(a)(1)(i)": "Contract clauses: wage rates and fringe benefits",
    "29 CFR 5.5(a)(1)(iii)": "Contract clauses: conformance (unlisted classifications)",
    "26 U.S.C. 45(b)(8)(A)": "Apprenticeship requirements: labor hours / applicable percentage",
    "26 U.S.C. 45(b)(8)(B)": "Apprenticeship requirements: apprentice-to-journeyworker ratio",
    "26 U.S.C. 45(b)(8)(C)": "Apprenticeship requirements: participation",
}


@dataclass(frozen=True)
class WageInput:
    classification: str
    base_rate: str
    fringe_rate: str = "0.00"


@dataclass(frozen=True)
class RatioInput:
    apprentice_hours: str
    total_hours: str
    required_ratio: str = REQUIRED_RATIO


@dataclass(frozen=True)
class Scenario:
    id: str
    area: Area
    rule: str
    citation: str
    description: str
    expected_compliant: bool
    wage: Optional[WageInput] = None
    ratio: Optional[RatioInput] = None
    # When set, the engine must raise this exception instead of returning a verdict.
    expected_error: Optional[ErrorName] = None
    tags: List[str] = field(default_factory=list)


SCENARIO_REGISTRY: List[Scenario] = [
    Scenario(
        id="PW-001",
        area="prevailing-wage",
        rule="Davis-Bacon: total compensation meets the prevailing wage",
        citation="29 CFR 5.5(a)(1)(i)",
        description="Base + fringe exactly meeting the required total is compliant",
        expected_compliant=True,
        wage=WageInput("Electrician", "45.00", "12.50"),
        tags=["happy-path"],
    ),
    Scenario(
        id="PW-002",
        area="prevailing-wage",
        rule="Davis-Bacon: underpayment of total compensation",
        citation="29 CFR 5.5(a)(1)(i)",
        description="Base + fringe below the required total is non-compliant",
        expected_compliant=False,
        wage=WageInput("Electrician", "40.00", "12.50"),
        tags=["violation", "money-impact"],
    ),
    Scenario(
        id="PW-003",
        area="prevailing-wage",
        rule="Davis-Bacon: fringe shortfall covered by extra base pay",
        citation="29 CFR 5.5(a)(1)(i)",
        description="Fringe below determination but extra base pay covers the total is compliant",
        expected_compliant=True,
        wage=WageInput("Electrician", "57.50", "0.00"),
        tags=["boundary", "fringe"],
    ),
    Scenario(
        id="PW-004",
        area="prevailing-wage",
        rule="Davis-Bacon: base-rate shortfall not curable by fringe",
        citation="29 CFR 5.5(a)(1)(i)",
        description="Below the basic rate is non-compliant even when fringe lifts the total",
        expected_compliant=False,
        wage=WageInput("Electrician", "40.00", "30.00"),
        tags=["violation", "fringe"],
    ),
    Scenario(
        id="PW-005",
        area="prevailing-wage",
        rule="Conformance: unlisted classification must fail loudly",
        citation="29 CFR 5.5(a)(1)(iii)",
        description="Unknown classification raises instead of silently passing",
        expected_compliant=False,
        wage=WageInput("Wizard", "99.00", "0.00"),
        expected_error="KeyError",
        tags=["failure-mode"],
    ),
    Scenario(
        id="AP-001",
        area="apprenticeship",
        rule="IRA apprenticeship labor-hours ratio met",
        citation="26 U.S.C. 45(b)(8)(A)",
        description="Apprentice-hours ratio exactly at the threshold is compliant",
        expected_compliant=True,
        ratio=RatioInput("15", "100", "0.15"),
        tags=["happy-path", "boundary"],
    ),
    Scenario(
        id="AP-002",
        area="apprenticeship",
        rule="IRA apprenticeship labor-hours ratio not met",
        citation="26 U.S.C. 45(b)(8)(A)",
        description="Apprentice-hours ratio below the threshold is non-compliant",
        expected_compliant=False,
        ratio=RatioInput("10", "100", "0.15"),
        tags=["violation", "money-impact"],
    ),
    Scenario(
        id="AP-003",
        area="apprenticeship",
        rule="IRA apprenticeship ratio: exact-fraction boundary",
        citation="26 U.S.C. 45(b)(8)(A)",
        description="0.3 of 3 hours is exactly 10% and compliant at a 10% threshold",
        expected_compliant=True,
        ratio=RatioInput("0.3", "3", "0.10"),
        tags=["boundary", "regression", "float-safety"],
    ),
    Scenario(
        id="PW-006",
        area="prevailing-wage",
        rule="Input integrity: sub-cent pay is rejected, not rounded",
        citation="29 CFR 5.5(a)(1)(i)",
        description="$44.995 base must not round up to $45.00 and pass; it is rejected",
        expected_compliant=False,
        wage=WageInput("Electrician", "44.995", "12.50"),
        expected_error="ValueError",
        tags=["failure-mode", "input-validation", "regression", "money-impact"],
    ),
    Scenario(
        id="PW-007",
        area="prevailing-wage",
        rule="Input integrity: negative fringe cannot offset base pay",
        citation="29 CFR 5.5(a)(1)(i)",
        description="A negative fringe amount is invalid payroll data and is rejected",
        expected_compliant=False,
        wage=WageInput("Electrician", "60.00", "-2.50"),
        expected_error="ValueError",
        tags=["failure-mode", "input-validation", "fringe"],
    ),
    Scenario(
        id="AP-004",
        area="apprenticeship",
        rule="Input integrity: apprentice hours cannot exceed total labor hours",
        citation="26 U.S.C. 45(b)(8)(A)",
        description="150 apprentice hours out of 100 total is impossible data and is rejected",
        expected_compliant=False,
        ratio=RatioInput("150", "100", "0.15"),
        expected_error="ValueError",
        tags=["failure-mode", "input-validation"],
    ),
    Scenario(
        id="AP-005",
        area="apprenticeship",
        rule="Input integrity: negative labor hours are rejected",
        citation="26 U.S.C. 45(b)(8)(A)",
        description="Negative apprentice hours are invalid timekeeping data and are rejected",
        expected_compliant=False,
        ratio=RatioInput("-5", "100", "0.15"),
        expected_error="ValueError",
        tags=["failure-mode", "input-validation"],
    ),
]


def scenarios_for(area: Area) -> List[Scenario]:
    return [s for s in SCENARIO_REGISTRY if s.area == area]
