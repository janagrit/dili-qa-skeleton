"""Scenario-driven unit tests: one test per registry scenario.

The expected verdict comes from the registry, so adding a scenario there adds a
test automatically (and a compliance reviewer can read every case without
reading test code). This includes AP-003, the 0.3/3 == 10% regression that the
original TypeScript engine got wrong.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from dili_compliance.registry import SCENARIO_REGISTRY

from .conftest import run_scenario

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("scenario", SCENARIO_REGISTRY, ids=lambda s: s.id)
def test_scenario_matches_expected_verdict(scenario, prevailing_rates):
    compliant, result = run_scenario(scenario, prevailing_rates)
    if scenario.expects_error:
        assert result is None  # the helper already asserted the raise
        return
    assert compliant is scenario.expected_compliant, (
        f"{scenario.id} ({scenario.citation}) expected "
        f"compliant={scenario.expected_compliant}, got {compliant}"
    )


def test_wage_shortfall_never_zero_when_noncompliant(prevailing_rates):
    """Regression for the TS bug: non-compliant must show a positive shortfall."""
    for scenario in SCENARIO_REGISTRY:
        if scenario.area != "prevailing-wage" or scenario.expects_error:
            continue
        compliant, result = run_scenario(scenario, prevailing_rates)
        if not compliant:
            assert result.shortfall_per_hour > Decimal("0.00"), scenario.id
