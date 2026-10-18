"""Combinatorial tests: full cross-product of inputs against an oracle.

Covers every combination of (base, fringe) pay positions relative to a
determination, instead of a handful of hand-picked examples.
"""

from __future__ import annotations

import itertools
from decimal import Decimal

import pytest

from dili_compliance.engine import PayrollRecord, PrevailingRate, check_prevailing_wage

pytestmark = pytest.mark.combinatorial

REQ_BASE = Decimal("45.00")
REQ_FRINGE = Decimal("12.50")

# Pay positions: below / exactly at / above the required figure.
OFFSETS = [Decimal("-5.00"), Decimal("0.00"), Decimal("5.00")]

CASES = list(itertools.product(OFFSETS, OFFSETS))


@pytest.mark.parametrize(
    "base_offset,fringe_offset", CASES, ids=[f"b{b}_f{f}" for b, f in CASES]
)
def test_base_and_fringe_combinations(base_offset, fringe_offset):
    rates = {"Electrician": PrevailingRate(base=REQ_BASE, fringe=REQ_FRINGE)}
    paid_base = REQ_BASE + base_offset
    paid_fringe = REQ_FRINGE + fringe_offset
    record = PayrollRecord.of("w", "Electrician", str(paid_base), str(paid_fringe))

    result = check_prevailing_wage(record, rates)

    # Oracle: compliant iff base meets base AND total meets total.
    meets_base = paid_base >= REQ_BASE
    meets_total = (paid_base + paid_fringe) >= (REQ_BASE + REQ_FRINGE)
    assert result.compliant == (meets_base and meets_total)
