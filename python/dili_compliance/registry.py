"""Scenario registry: the executable specification of the compliance engine.

Every rule becomes a cited, deterministic scenario an auditor can trace:
scenario id -> rule -> paragraph-level citation -> inputs -> expected result.

Unlike the TypeScript skeleton, the inputs and the expected verdict live here in
the registry (not hard-coded in test bodies), so a compliance reviewer can read
and add scenarios without touching test code. Citations are paragraph-level per
the audit (e.g. ``29 CFR 5.5(a)(1)(i)``), not just ``29 CFR Part 5``.
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

# Illustrative apprenticeship labor-hours ratio (IRA good-faith threshold era).
REQUIRED_RATIO = "0.15"


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
    expects_error: bool = False
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
        citation="29 CFR 5.5(a)(1)(ii)",
        description="Unknown classification raises instead of silently passing",
        expected_compliant=False,
        wage=WageInput("Wizard", "99.00", "0.00"),
        expects_error=True,
        tags=["failure-mode"],
    ),
    Scenario(
        id="AP-001",
        area="apprenticeship",
        rule="IRA apprenticeship labor-hours ratio met",
        citation="26 U.S.C. 45(b)(8)(B)",
        description="Apprentice-hours ratio exactly at the threshold is compliant",
        expected_compliant=True,
        ratio=RatioInput("15", "100", "0.15"),
        tags=["happy-path", "boundary"],
    ),
    Scenario(
        id="AP-002",
        area="apprenticeship",
        rule="IRA apprenticeship labor-hours ratio not met",
        citation="26 U.S.C. 45(b)(8)(B)",
        description="Apprentice-hours ratio below the threshold is non-compliant",
        expected_compliant=False,
        ratio=RatioInput("10", "100", "0.15"),
        tags=["violation", "money-impact"],
    ),
    Scenario(
        id="AP-003",
        area="apprenticeship",
        rule="IRA apprenticeship ratio: exact-fraction boundary",
        citation="26 U.S.C. 45(b)(8)(B)",
        description="0.3 of 3 hours is exactly 10% and compliant at a 10% threshold",
        expected_compliant=True,
        ratio=RatioInput("0.3", "3", "0.10"),
        tags=["boundary", "regression", "float-safety"],
    ),
]


def scenarios_for(area: Area) -> List[Scenario]:
    return [s for s in SCENARIO_REGISTRY if s.area == area]
