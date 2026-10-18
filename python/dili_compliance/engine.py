"""Illustrative prevailing-wage / apprenticeship compliance engine (Python port).

This is NOT Dili's real logic and NOT legal advice. It mirrors the TypeScript
stub in ``src/complianceEngine.ts`` but fixes the two verdict bugs found in the
audit and adds the Davis-Bacon fringe component:

* Money is handled in integer cents (via ``Decimal``) so a worker is never
  flagged non-compliant with a ``$0.00`` shortfall.
* The apprenticeship ratio is compared with exact ``Fraction`` arithmetic, so an
  input that is exactly at the threshold (e.g. 0.3 / 3 == 10%) is compliant, and
  the compared value and the displayed value never disagree.
* The wage check scores total compensation (base + fringe), not base alone,
  which is what Davis-Bacon actually requires.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from typing import Mapping, Union

Number = Union[int, float, str, Decimal]


def _money(value: Number) -> Decimal:
    """Coerce a value to a 2dp Decimal (cents). Strings avoid float artefacts."""
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class PrevailingRate:
    """A Davis-Bacon wage determination line: basic rate plus fringe."""

    base: Decimal
    fringe: Decimal

    @property
    def total(self) -> Decimal:
        return self.base + self.fringe

    @classmethod
    def of(cls, base: Number, fringe: Number = 0) -> "PrevailingRate":
        return cls(base=_money(base), fringe=_money(fringe))


@dataclass(frozen=True)
class PayrollRecord:
    worker_id: str
    classification: str
    base_rate: Decimal
    fringe_rate: Decimal
    hours_worked: Decimal

    @classmethod
    def of(
        cls,
        worker_id: str,
        classification: str,
        base_rate: Number,
        fringe_rate: Number = 0,
        hours_worked: Number = 0,
    ) -> "PayrollRecord":
        return cls(
            worker_id=worker_id,
            classification=classification,
            base_rate=_money(base_rate),
            fringe_rate=_money(fringe_rate),
            hours_worked=_money(hours_worked),
        )


@dataclass(frozen=True)
class WageCheckResult:
    compliant: bool
    required_base: Decimal
    required_total: Decimal
    paid_base: Decimal
    paid_total: Decimal
    shortfall_per_hour: Decimal


def check_prevailing_wage(
    record: PayrollRecord,
    prevailing_rates: Mapping[str, PrevailingRate],
) -> WageCheckResult:
    """Davis-Bacon check on total compensation (base + fringe).

    A worker is compliant when total compensation meets the required total AND
    base pay meets the required basic rate: fringe cannot paper over a base-rate
    shortfall, but extra base pay can offset a fringe shortfall.

    Reference: 29 CFR 5.5(a)(1)(i) (basic hourly rate + fringe benefits).
    """
    if record.classification not in prevailing_rates:
        raise KeyError(
            f"No prevailing rate for classification: {record.classification}"
        )
    rate = prevailing_rates[record.classification]

    paid_base = record.base_rate
    paid_total = record.base_rate + record.fringe_rate

    base_shortfall = max(Decimal("0.00"), rate.base - paid_base)
    total_shortfall = max(Decimal("0.00"), rate.total - paid_total)
    shortfall = max(base_shortfall, total_shortfall)

    return WageCheckResult(
        compliant=shortfall == Decimal("0.00"),
        required_base=rate.base,
        required_total=rate.total,
        paid_base=paid_base,
        paid_total=paid_total,
        shortfall_per_hour=shortfall,
    )


@dataclass(frozen=True)
class ApprenticeshipCheckResult:
    compliant: bool
    actual_ratio: Fraction
    required_ratio: Fraction
    displayed_ratio: Decimal


def check_apprenticeship_ratio(
    apprentice_hours: Number,
    total_hours: Number,
    required_ratio: Number,
) -> ApprenticeshipCheckResult:
    """Apprentice hours as a share of total hours must meet the required ratio.

    Uses exact ``Fraction`` arithmetic so a value exactly at the threshold is
    compliant and the verdict never contradicts the displayed ratio.

    Reference: 26 U.S.C. 45(b)(8)(B) (apprenticeship labor-hours ratio);
    see also IRS Notice 2022-61.
    """
    total = Fraction(str(total_hours))
    if total <= 0:
        raise ValueError("total_hours must be positive")

    actual = Fraction(str(apprentice_hours)) / total
    required = Fraction(str(required_ratio))
    displayed = Decimal(actual.numerator) / Decimal(actual.denominator)

    return ApprenticeshipCheckResult(
        compliant=actual >= required,
        actual_ratio=actual,
        required_ratio=required,
        displayed_ratio=displayed.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
    )
