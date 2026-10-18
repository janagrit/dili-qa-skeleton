"""Illustrative Dili prevailing-wage / apprenticeship compliance engine (Python)."""

from .engine import (
    ApprenticeshipCheckResult,
    PayrollRecord,
    PrevailingRate,
    WageCheckResult,
    check_apprenticeship_ratio,
    check_prevailing_wage,
)
from .registry import SCENARIO_REGISTRY, Scenario, scenarios_for

__all__ = [
    "ApprenticeshipCheckResult",
    "PayrollRecord",
    "PrevailingRate",
    "WageCheckResult",
    "check_apprenticeship_ratio",
    "check_prevailing_wage",
    "SCENARIO_REGISTRY",
    "Scenario",
    "scenarios_for",
]
