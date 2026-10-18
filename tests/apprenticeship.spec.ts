import { test, expect } from '@playwright/test';
import { checkApprenticeshipRatio } from '../src/complianceEngine';
import { scenariosFor } from '../src/scenarioRegistry';

// Illustrative threshold only. The real value comes from the statute.
const REQUIRED_RATIO = 0.15;

for (const scenario of scenariosFor('apprenticeship')) {
  test(`[${scenario.id}] ${scenario.description} (${scenario.citation})`, async () => {
    switch (scenario.id) {
      case 'AP-001': {
        const result = checkApprenticeshipRatio(15, 100, REQUIRED_RATIO);
        expect(result.compliant).toBe(true);
        break;
      }
      case 'AP-002': {
        const result = checkApprenticeshipRatio(10, 100, REQUIRED_RATIO);
        expect(result.compliant).toBe(false);
        expect(result.actualRatio).toBeLessThan(REQUIRED_RATIO);
        break;
      }
      case 'AP-003': {
        const result = checkApprenticeshipRatio(0.3, 3, 0.1);
        expect(result.compliant).toBe(true);
        break;
      }
      case 'AP-004': {
        expect(() => checkApprenticeshipRatio(150, 100, REQUIRED_RATIO)).toThrow(/exceed totalHours/);
        expect(() => checkApprenticeshipRatio(-5, 100, REQUIRED_RATIO)).toThrow(/non-negative/);
        break;
      }
      default:
        throw new Error(`No test body for scenario ${scenario.id} yet: add it here`);
    }
  });
}
