import { test, expect } from '@playwright/test';
import { checkPrevailingWage, PayrollRecord } from '../src/complianceEngine';
import { scenariosFor } from '../src/scenarioRegistry';

// Illustrative rates only. In the real system these come from wage determinations.
const RATES: Record<string, number> = {
  Electrician: 45.0,
  Laborer: 28.5,
};

function record(overrides: Partial<PayrollRecord> = {}): PayrollRecord {
  return {
    workerId: 'w-1',
    classification: 'Electrician',
    hourlyRate: 45.0,
    hoursWorked: 40,
    ...overrides,
  };
}

for (const scenario of scenariosFor('prevailing-wage')) {
  test(`[${scenario.id}] ${scenario.description} (${scenario.citation})`, async () => {
    switch (scenario.id) {
      case 'PW-001': {
        const result = checkPrevailingWage(record({ hourlyRate: 45.0 }), RATES);
        expect(result.compliant).toBe(true);
        expect(result.shortfallPerHour).toBe(0);
        break;
      }
      case 'PW-002': {
        const result = checkPrevailingWage(record({ hourlyRate: 40.0 }), RATES);
        expect(result.compliant).toBe(false);
        expect(result.shortfallPerHour).toBe(5.0);
        break;
      }
      case 'PW-008': {
        const result = checkPrevailingWage(record({ hourlyRate: 50.0 }), RATES);
        expect(result.compliant).toBe(true);
        break;
      }
      case 'PW-005': {
        expect(() => checkPrevailingWage(record({ classification: 'Wizard' }), RATES)).toThrow(
          /No prevailing rate/,
        );
        break;
      }
      case 'PW-006': {
        expect(() => checkPrevailingWage(record({ hourlyRate: 44.995 }), RATES)).toThrow(
          /fractions of a cent/,
        );
        // A cent-level underpayment still yields a positive shortfall, never $0.
        const result = checkPrevailingWage(record({ hourlyRate: 44.99 }), RATES);
        expect(result.compliant).toBe(false);
        expect(result.shortfallPerHour).toBe(0.01);
        break;
      }
      default:
        throw new Error(`No test body for scenario ${scenario.id} yet: add it here`);
    }
  });
}
