"""Shared fixtures and registry-aware helpers for the compliance test suite."""

from __future__ import annotations

from decimal import Decimal
from typing import Dict

import pytest

from dili_compliance.engine import (
    PayrollRecord,
    PrevailingRate,
    check_apprenticeship_ratio,
    check_prevailing_wage,
)
from dili_compliance.registry import RATES, Scenario


@pytest.fixture(scope="session")
def prevailing_rates() -> Dict[str, PrevailingRate]:
    return {name: PrevailingRate.of(base, fringe) for name, (base, fringe) in RATES.items()}


def run_scenario(scenario: Scenario, prevailing_rates: Dict[str, PrevailingRate]):
    """Execute a registry scenario and return (compliant, result).

    Raising scenarios return (False, None) after asserting the error type.
    """
    if scenario.area == "prevailing-wage":
        assert scenario.wage is not None, f"{scenario.id} missing wage input"
        record = PayrollRecord.of(
            worker_id=scenario.id,
            classification=scenario.wage.classification,
            base_rate=scenario.wage.base_rate,
            fringe_rate=scenario.wage.fringe_rate,
        )
        if scenario.expects_error:
            with pytest.raises(KeyError):
                check_prevailing_wage(record, prevailing_rates)
            return (False, None)
        result = check_prevailing_wage(record, prevailing_rates)
        return (result.compliant, result)

    assert scenario.ratio is not None, f"{scenario.id} missing ratio input"
    result = check_apprenticeship_ratio(
        scenario.ratio.apprentice_hours,
        scenario.ratio.total_hours,
        scenario.ratio.required_ratio,
    )
    return (result.compliant, result)


@pytest.fixture
def cents():
    return lambda v: Decimal(str(v)).quantize(Decimal("0.01"))
