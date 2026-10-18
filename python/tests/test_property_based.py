"""Property-based tests (Hypothesis).

These assert invariants across the whole input range, which is what catches the
two floating-point verdict bugs the audit found — bugs the example-based tests
missed because they only used clean inputs.
"""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction

import pytest
from hypothesis import given
from hypothesis import strategies as st

from dili_compliance.engine import (
    PayrollRecord,
    PrevailingRate,
    check_apprenticeship_ratio,
    check_prevailing_wage,
)

pytestmark = pytest.mark.property

# Money strategy: 0.00 .. 500.00 in whole cents, as strings to stay exact.
cents = st.integers(min_value=0, max_value=50_000).map(lambda c: f"{c / 100:.2f}")
hours = st.integers(min_value=1, max_value=10_000)


@given(req_base=cents, req_fringe=cents, paid_base=cents, paid_fringe=cents)
def test_wage_verdict_and_shortfall_are_consistent(req_base, req_fringe, paid_base, paid_fringe):
    rates = {"X": PrevailingRate.of(req_base, req_fringe)}
    record = PayrollRecord.of("w", "X", paid_base, paid_fringe)
    result = check_prevailing_wage(record, rates)

    # Invariant 1: a non-compliant verdict always has a positive shortfall,
    # and a compliant verdict always has exactly zero. (The TS bug broke this.)
    if result.compliant:
        assert result.shortfall_per_hour == Decimal("0.00")
    else:
        assert result.shortfall_per_hour > Decimal("0.00")

    # Invariant 2: compliant iff base meets base AND total meets total.
    meets_base = Decimal(paid_base) >= Decimal(req_base)
    meets_total = (Decimal(paid_base) + Decimal(paid_fringe)) >= (
        Decimal(req_base) + Decimal(req_fringe)
    )
    assert result.compliant == (meets_base and meets_total)


@st.composite
def apprentice_and_total(draw):
    total = draw(hours)
    return draw(st.integers(min_value=0, max_value=total)), total


@given(pair=apprentice_and_total(), req_num=st.integers(1, 99))
def test_ratio_verdict_matches_exact_comparison(pair, req_num):
    apprentice, total = pair
    required = Fraction(req_num, 100)
    result = check_apprenticeship_ratio(apprentice, total, str(required))
    exact = Fraction(apprentice, total)
    # Verdict must equal the exact rational comparison — no float drift.
    assert result.compliant == (exact >= required)


@given(k=st.integers(min_value=1, max_value=1000), req_num=st.integers(1, 99))
def test_exact_threshold_is_compliant(k, req_num):
    """A worker exactly at the threshold is compliant (the 0.3/3 == 10% case).

    Build exact-ratio inputs directly (apprentice = req_num*k, total = 100*k) so
    the ratio equals the threshold with no rounding and no filtering.
    """
    required = Fraction(req_num, 100)
    result = check_apprenticeship_ratio(req_num * k, 100 * k, str(required))
    assert result.compliant is True
