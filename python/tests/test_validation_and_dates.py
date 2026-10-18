"""Input validation and effective-date rules.

Invalid payroll or timekeeping data must be rejected, never turned into a
compliance verdict. The apprenticeship percentage depends on when construction
began (26 U.S.C. 45(b)(8)(A)(ii)).
"""

from __future__ import annotations

from datetime import date
from fractions import Fraction

import pytest
from hypothesis import given
from hypothesis import strategies as st

from dili_compliance.engine import (
    PayrollRecord,
    PrevailingRate,
    applicable_percentage,
    check_apprenticeship_ratio,
    check_prevailing_wage,
)

pytestmark = pytest.mark.unit

RATES = {"Electrician": PrevailingRate.of("45.00", "12.50")}


@pytest.mark.parametrize(
    "base,fringe",
    [("44.995", "12.50"), ("45.00", "12.501"), ("-1.00", "100.00"), ("60.00", "-2.50"),
     ("nan", "0"), ("inf", "0"), ("abc", "0")],
    ids=["sub-cent-base", "sub-cent-fringe", "negative-base", "negative-fringe",
         "nan", "inf", "not-a-number"],
)
def test_invalid_pay_is_rejected(base, fringe):
    with pytest.raises(ValueError):
        PayrollRecord.of("w", "Electrician", base, fringe)


def test_negative_hours_worked_rejected():
    with pytest.raises(ValueError):
        PayrollRecord.of("w", "Electrician", "45.00", "12.50", hours_worked="-1")


def test_sub_cent_prevailing_rate_rejected():
    with pytest.raises(ValueError):
        PrevailingRate.of("45.005", "0")


@pytest.mark.parametrize(
    "apprentice,total,required",
    [("150", "100", "0.15"), ("-5", "100", "0.15"), ("5", "-100", "0.15"),
     ("0", "0", "0.15"), ("10", "100", "1.5"), ("10", "100", "-0.1"), ("nan", "3", "0.1")],
    ids=["apprentice-over-total", "negative-apprentice", "negative-total", "zero-total",
         "ratio-over-100pct", "negative-ratio", "nan"],
)
def test_invalid_ratio_inputs_rejected(apprentice, total, required):
    with pytest.raises(ValueError):
        check_apprenticeship_ratio(apprentice, total, required)


def test_whole_cent_values_still_accepted():
    result = check_prevailing_wage(PayrollRecord.of("w", "Electrician", "45", "12.5"), RATES)
    assert result.compliant is True


@given(cents=st.integers(min_value=0, max_value=10_000_000), mills=st.integers(1, 9))
def test_any_sub_cent_amount_is_rejected(cents, mills):
    amount = f"{cents // 100}.{cents % 100:02d}{mills}"
    with pytest.raises(ValueError):
        PayrollRecord.of("w", "Electrician", amount, "0")


@pytest.mark.parametrize(
    "start,expected",
    [
        (date(2022, 12, 31), Fraction(10, 100)),
        (date(2023, 1, 1), Fraction(125, 1000)),
        (date(2023, 12, 31), Fraction(125, 1000)),
        (date(2024, 1, 1), Fraction(15, 100)),
    ],
    ids=["last-day-2022", "first-day-2023", "last-day-2023", "first-day-2024"],
)
def test_applicable_percentage_boundaries(start, expected):
    """26 U.S.C. 45(b)(8)(A)(ii): 10% / 12.5% / 15% by construction start."""
    assert applicable_percentage(start) == expected


def test_same_hours_change_verdict_with_start_date():
    """12 of 100 hours passes for a 2022 start but fails for a 2024 start."""
    early = check_apprenticeship_ratio("12", "100", applicable_percentage(date(2022, 6, 1)))
    late = check_apprenticeship_ratio("12", "100", applicable_percentage(date(2024, 6, 1)))
    assert early.compliant is True
    assert late.compliant is False
