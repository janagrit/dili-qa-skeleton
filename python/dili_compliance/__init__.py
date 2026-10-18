"""Illustrative Dili prevailing-wage / apprenticeship compliance engine (Python)."""

from .engine import (
    ApprenticeshipCheckResult,
    PayrollRecord,
    PrevailingRate,
    WageCheckResult,
    applicable_percentage,
    check_apprenticeship_ratio,
    check_prevailing_wage,
)
from .registry import CITATIONS, SCENARIO_REGISTRY, Scenario, scenarios_for

__all__ = [
    "ApprenticeshipCheckResult",
    "PayrollRecord",
    "PrevailingRate",
    "WageCheckResult",
    "applicable_percentage",
    "check_apprenticeship_ratio",
    "check_prevailing_wage",
    "CITATIONS",
    "SCENARIO_REGISTRY",
    "Scenario",
    "scenarios_for",
]
