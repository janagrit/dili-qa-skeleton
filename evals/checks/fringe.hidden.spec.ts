import { test, expect } from '@playwright/test';
import { checkPrevailingWage } from '../src/complianceEngine';

/**
 * Hidden judge for the ts-fringe-support eval task. Copied into tests/ only
 * at judge time, so the agent never sees it. Mirrors python/dili_compliance.
 */
const rates = { Electrician: { base: 40, fringe: 10 }, Laborer: 30 };
const worker = { workerId: 'W1', classification: 'Electrician', hoursWorked: 8 };

test('fringe: base + fringe at the required total is compliant', () => {
  const r = checkPrevailingWage({ ...worker, hourlyRate: 40, fringeRate: 10 }, rates);
  expect(r.compliant).toBe(true);
  expect(r.shortfallPerHour).toBe(0);
});

test('fringe: fringe shortfall is non-compliant', () => {
  const r = checkPrevailingWage({ ...worker, hourlyRate: 40, fringeRate: 7.5 }, rates);
  expect(r.compliant).toBe(false);
  expect(r.shortfallPerHour).toBe(2.5);
});

test('fringe: extra base pay covers a fringe shortfall', () => {
  const r = checkPrevailingWage({ ...worker, hourlyRate: 45, fringeRate: 5 }, rates);
  expect(r.compliant).toBe(true);
});

test('fringe: extra fringe cannot cover a base shortfall', () => {
  const r = checkPrevailingWage({ ...worker, hourlyRate: 38, fringeRate: 20 }, rates);
  expect(r.compliant).toBe(false);
  expect(r.shortfallPerHour).toBe(2);
});

test('fringe: omitted fringeRate and plain-number rates keep base-only behaviour', () => {
  const r = checkPrevailingWage({ ...worker, classification: 'Laborer', hourlyRate: 29 }, rates);
  expect(r.compliant).toBe(false);
  expect(r.shortfallPerHour).toBe(1);
});

test('fringe: sub-cent fringe is rejected', () => {
  expect(() =>
    checkPrevailingWage({ ...worker, hourlyRate: 40, fringeRate: 10.005 }, rates),
  ).toThrow();
});
