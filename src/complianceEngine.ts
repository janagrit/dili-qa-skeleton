/**
 * Illustrative stub of a prevailing-wage / apprenticeship compliance engine.
 *
 * This is NOT Dili's real logic and NOT legal advice. The Python port in
 * `python/dili_compliance` is the reference implementation (it also scores
 * fringe benefits); this file keeps the TypeScript side correct:
 *
 * - Money is compared in integer cents, so a non-compliant verdict always has
 *   a positive shortfall and sub-cent inputs are rejected, never rounded.
 * - The apprenticeship check compares apprentice hours with
 *   requiredRatio * totalHours using a tiny tolerance, so 0.3 / 3 at 10% is
 *   compliant despite binary floating point.
 * - Invalid inputs (negative, NaN/Infinity, apprentice hours above total)
 *   throw instead of producing a verdict.
 */

export interface PayrollRecord {
  workerId: string;
  classification: string; // e.g. "Electrician"
  hourlyRate: number; // actually paid, USD
  hoursWorked: number;
}

export interface WageCheckResult {
  compliant: boolean;
  requiredRate: number;
  paidRate: number;
  shortfallPerHour: number;
}

/** Float tolerance for values that should be whole cents / exact ratios. */
const EPSILON = 1e-9;

function assertNonNegative(value: number, field: string): void {
  if (!Number.isFinite(value) || value < 0) {
    throw new Error(`${field} must be a finite, non-negative number (got ${value})`);
  }
}

/** Convert dollars to integer cents, rejecting fractions of a cent. */
export function toCents(dollars: number, field = 'amount'): number {
  assertNonNegative(dollars, field);
  const cents = Math.round(dollars * 100);
  if (Math.abs(dollars * 100 - cents) > EPSILON * Math.max(1, cents)) {
    throw new Error(`${field} has fractions of a cent (got ${dollars})`);
  }
  return cents;
}

/** A worker is compliant when paid at or above the prevailing rate (29 CFR 5.5(a)(1)(i)). */
export function checkPrevailingWage(
  record: PayrollRecord,
  prevailingRates: Record<string, number>,
): WageCheckResult {
  const requiredRate = prevailingRates[record.classification];
  if (requiredRate === undefined) {
    throw new Error(`No prevailing rate for classification: ${record.classification}`);
  }
  assertNonNegative(record.hoursWorked, 'hoursWorked');
  const requiredCents = toCents(requiredRate, 'requiredRate');
  const paidCents = toCents(record.hourlyRate, 'hourlyRate');
  const shortfallCents = Math.max(0, requiredCents - paidCents);
  return {
    compliant: shortfallCents === 0,
    requiredRate,
    paidRate: record.hourlyRate,
    shortfallPerHour: shortfallCents / 100,
  };
}

export interface ApprenticeshipCheckResult {
  compliant: boolean;
  actualRatio: number;
  requiredRatio: number;
}

/**
 * Apprentice hours as a share of total labor hours must meet the applicable
 * percentage (26 U.S.C. 45(b)(8)(A)).
 */
export function checkApprenticeshipRatio(
  apprenticeHours: number,
  totalHours: number,
  requiredRatio: number,
): ApprenticeshipCheckResult {
  assertNonNegative(apprenticeHours, 'apprenticeHours');
  assertNonNegative(totalHours, 'totalHours');
  assertNonNegative(requiredRatio, 'requiredRatio');
  if (totalHours === 0) {
    throw new Error('totalHours must be positive');
  }
  if (apprenticeHours > totalHours) {
    throw new Error(`apprenticeHours (${apprenticeHours}) exceed totalHours (${totalHours})`);
  }
  if (requiredRatio > 1) {
    throw new Error(`requiredRatio must be between 0 and 1 (got ${requiredRatio})`);
  }
  const requiredHours = requiredRatio * totalHours;
  return {
    compliant: apprenticeHours >= requiredHours - EPSILON * Math.max(1, requiredHours),
    actualRatio: Math.round((apprenticeHours / totalHours) * 10000) / 10000,
    requiredRatio,
  };
}
