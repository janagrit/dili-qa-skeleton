/**
 * Illustrative stub of a prevailing-wage / apprenticeship compliance engine.
 *
 * This is NOT Dili's real logic and NOT legal advice. It exists so the
 * skeleton has something small and deterministic to test against.
 * Replace it with the real engine (or API calls) when extending.
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

/** A worker is compliant when paid at or above the prevailing rate. */
export function checkPrevailingWage(
  record: PayrollRecord,
  prevailingRates: Record<string, number>,
): WageCheckResult {
  const requiredRate = prevailingRates[record.classification];
  if (requiredRate === undefined) {
    throw new Error(`No prevailing rate for classification: ${record.classification}`);
  }
  const shortfall = Math.max(0, requiredRate - record.hourlyRate);
  return {
    compliant: shortfall === 0,
    requiredRate,
    paidRate: record.hourlyRate,
    shortfallPerHour: Math.round(shortfall * 100) / 100,
  };
}

export interface ApprenticeshipCheckResult {
  compliant: boolean;
  actualRatio: number;
  requiredRatio: number;
}

/** Apprentice hours as a share of total hours must meet the required ratio. */
export function checkApprenticeshipRatio(
  apprenticeHours: number,
  totalHours: number,
  requiredRatio: number,
): ApprenticeshipCheckResult {
  if (totalHours <= 0) {
    throw new Error('totalHours must be positive');
  }
  const actualRatio = apprenticeHours / totalHours;
  return {
    compliant: actualRatio >= requiredRatio,
    actualRatio: Math.round(actualRatio * 10000) / 10000,
    requiredRatio,
  };
}
