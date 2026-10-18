"""Execute registry scenarios against the engine.

Kept out of ``conftest.py`` so tests, reports and ad-hoc scripts can all import
it the same way.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional, Union

from .engine import (
    ApprenticeshipCheckResult,
    PayrollRecord,
    PrevailingRate,
    WageCheckResult,
    check_apprenticeship_ratio,
    check_prevailing_wage,
)
from .registry import RATES, Scenario


@dataclass(frozen=True)
class ScenarioOutcome:
    compliant: Optional[bool]
    result: Optional[Union[WageCheckResult, ApprenticeshipCheckResult]]
    error: Optional[Exception] = None


def default_rates() -> dict:
    return {name: PrevailingRate.of(base, fringe) for name, (base, fringe) in RATES.items()}


def run_scenario(
    scenario: Scenario, prevailing_rates: Optional[Mapping[str, PrevailingRate]] = None
) -> ScenarioOutcome:
    """Run one scenario. Exceptions are captured, not raised, so callers can
    compare them with ``scenario.expected_error``."""
    rates = prevailing_rates if prevailing_rates is not None else default_rates()
    try:
        if scenario.area == "prevailing-wage":
            if scenario.wage is None:
                raise AssertionError(f"{scenario.id} missing wage input")
            record = PayrollRecord.of(
                worker_id=scenario.id,
                classification=scenario.wage.classification,
                base_rate=scenario.wage.base_rate,
                fringe_rate=scenario.wage.fringe_rate,
            )
            result = check_prevailing_wage(record, rates)
        else:
            if scenario.ratio is None:
                raise AssertionError(f"{scenario.id} missing ratio input")
            result = check_apprenticeship_ratio(
                scenario.ratio.apprentice_hours,
                scenario.ratio.total_hours,
                scenario.ratio.required_ratio,
            )
    except (KeyError, ValueError) as exc:
        return ScenarioOutcome(compliant=None, result=None, error=exc)
    return ScenarioOutcome(compliant=result.compliant, result=result)
