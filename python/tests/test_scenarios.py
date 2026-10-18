"""Scenario-driven unit tests: one test per registry scenario.

The expected verdict (or expected rejection) comes from the registry, so adding
a scenario there adds a test automatically and a compliance reviewer can read
every case without reading test code. Includes AP-003 (the 0.3/3 == 10%
regression) and PW-006 (the $44.995 sub-cent rounding regression).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from dili_compliance.registry import SCENARIO_REGISTRY
from dili_compliance.runner import run_scenario

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("scenario", SCENARIO_REGISTRY, ids=lambda s: s.id)
def test_scenario_matches_expected_outcome(scenario, prevailing_rates):
    outcome = run_scenario(scenario, prevailing_rates)
    trace = f"{scenario.id} ({scenario.citation})"

    if scenario.expected_error:
        assert outcome.error is not None, f"{trace} expected {scenario.expected_error}, got a verdict"
        assert type(outcome.error).__name__ == scenario.expected_error, (
            f"{trace} expected {scenario.expected_error}, got {type(outcome.error).__name__}: "
            f"{outcome.error}"
        )
        return

    assert outcome.error is None, f"{trace} raised unexpectedly: {outcome.error!r}"
    assert outcome.compliant is scenario.expected_compliant, (
        f"{trace} expected compliant={scenario.expected_compliant}, got {outcome.compliant}"
    )


def test_wage_shortfall_never_zero_when_noncompliant(prevailing_rates):
    """Regression for the TS bug: non-compliant must show a positive shortfall."""
    for scenario in SCENARIO_REGISTRY:
        if scenario.area != "prevailing-wage" or scenario.expected_error:
            continue
        outcome = run_scenario(scenario, prevailing_rates)
        if not outcome.compliant:
            assert outcome.result.shortfall_per_hour > Decimal("0.00"), scenario.id
