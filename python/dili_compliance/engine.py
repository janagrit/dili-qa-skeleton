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
* Invalid input is rejected with ``ValueError`` instead of producing a verdict:
  sub-cent money (no silent rounding), negative amounts or hours, NaN/inf,
  apprentice hours above total hours, and ratios above 100%.
* The apprenticeship percentage depends on the construction start date
  (``applicable_percentage``).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from datetime import date
from fractions import Fraction
from typing import Mapping, Union

Number = Union[int, float, str, Decimal]


CENT = Decimal("0.01")


def _decimal(value: Number, field: str) -> Decimal:
    """Parse a finite, non-negative Decimal. Strings avoid float artefacts."""
    try:
        d = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{field} is not a number: {value!r}") from exc
    if not d.is_finite():
        raise ValueError(f"{field} must be finite, got {value!r}")
    if d < 0:
        raise ValueError(f"{field} must not be negative, got {value!r}")
    return d


def _fraction(value: Union[Number, Fraction], field: str) -> Fraction:
    """Parse an exact, non-negative rational (accepts "0.15", "3/20", Fraction)."""
    try:
        f = Fraction(str(value))
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"{field} is not a finite number: {value!r}") from exc
    if f < 0:
        raise ValueError(f"{field} must not be negative, got {value!r}")
    return f


def _money(value: Number, field: str = "amount") -> Decimal:
    """Parse a money amount in whole cents.

    Sub-cent amounts are rejected rather than rounded: rounding 44.995 up to
    45.00 before comparing would silently turn an underpayment into a pass.
    """
    d = _decimal(value, field)
    if d != d.quantize(CENT):
        raise ValueError(f"{field} has fractions of a cent: {value!r}")
    return d.quantize(CENT)


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
        return cls(base=_money(base, "base"), fringe=_money(fringe, "fringe"))


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
            base_rate=_money(base_rate, "base_rate"),
            fringe_rate=_money(fringe_rate, "fringe_rate"),
            hours_worked=_decimal(hours_worked, "hours_worked"),
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

    Reference: 26 U.S.C. 45(b)(8)(A) (labor-hours requirement / applicable
    percentage). 45(b)(8)(B) is the separate apprentice-to-journeyworker ratio.
    """
    apprentice = _fraction(apprentice_hours, "apprentice_hours")
    total = _fraction(total_hours, "total_hours")
    required = _fraction(required_ratio, "required_ratio")
    if total == 0:
        raise ValueError("total_hours must be positive")
    if apprentice > total:
        raise ValueError(
            f"apprentice_hours ({apprentice_hours}) exceed total_hours ({total_hours})"
        )
    if required > 1:
        raise ValueError(f"required_ratio must be between 0 and 1, got {required_ratio}")

    actual = apprentice / total
    displayed = Decimal(actual.numerator) / Decimal(actual.denominator)

    return ApprenticeshipCheckResult(
        compliant=actual >= required,
        actual_ratio=actual,
        required_ratio=required,
        displayed_ratio=displayed.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
    )


def applicable_percentage(construction_start: date) -> Fraction:
    """Apprentice labor-hours percentage by construction start date.

    26 U.S.C. 45(b)(8)(A)(ii): 10% if construction begins before 2023, 12.5% if
    it begins during 2023, 15% if it begins after 2023.
    """
    if construction_start < date(2023, 1, 1):
        return Fraction(10, 100)
    if construction_start <= date(2023, 12, 31):
        return Fraction(125, 1000)
    return Fraction(15, 100)
