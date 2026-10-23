/**
 * Scenario registry: the executable specification of the compliance engine.
 *
 * Every rule from the source regulation becomes a cited, deterministic test
 * scenario. An auditor can follow any test failure back to the rule it
 * violates: scenario id -> rule -> citation.
 *
 * IDs are shared with python/dili_compliance/registry.py: one ID = one rule in
 * both ports. This port covers a subset (no fringe), so numbering has gaps.
 */

export interface TestScenario {
  id: string;
  area: 'prevailing-wage' | 'apprenticeship';
  rule: string;
  /** Paragraph-level citation. Rates and thresholds in tests are illustrative. */
  citation: string;
  description: string;
  tags: string[];
}

export const scenarioRegistry: TestScenario[] = [
  {
    id: 'PW-001',
    area: 'prevailing-wage',
    rule: 'Davis-Bacon Act',
    citation: '29 CFR 5.5(a)(1)(i)',
    description: 'Worker paid exactly the prevailing rate is compliant',
    tags: ['happy-path'],
  },
  {
    id: 'PW-002',
    area: 'prevailing-wage',
    rule: 'Davis-Bacon Act',
    citation: '29 CFR 5.5(a)(1)(i)',
    description: 'Worker paid below the prevailing rate is non-compliant with a computed shortfall',
    tags: ['violation', 'money-impact'],
  },
  {
    id: 'PW-008',
    area: 'prevailing-wage',
    rule: 'Davis-Bacon Act',
    citation: '29 CFR 5.5(a)(1)(i)',
    description: 'Worker paid above the prevailing rate is compliant',
    tags: ['boundary'],
  },
  {
    id: 'PW-005',
    area: 'prevailing-wage',
    rule: 'Davis-Bacon Act: conformance of unlisted classifications',
    citation: '29 CFR 5.5(a)(1)(iii)',
    description: 'Unknown worker classification fails loudly instead of silently passing',
    tags: ['failure-mode'],
  },
  {
    id: 'AP-001',
    area: 'apprenticeship',
    rule: 'IRA apprenticeship labor-hours requirement',
    citation: '26 U.S.C. 45(b)(8)(A)',
    description: 'Apprentice-hours ratio at the required threshold is compliant',
    tags: ['happy-path'],
  },
  {
    id: 'AP-002',
    area: 'apprenticeship',
    rule: 'IRA apprenticeship labor-hours requirement',
    citation: '26 U.S.C. 45(b)(8)(A)',
    description: 'Apprentice-hours ratio below the required threshold is non-compliant',
    tags: ['violation', 'money-impact'],
  },
  {
    id: 'AP-003',
    area: 'apprenticeship',
    rule: 'IRA apprenticeship labor-hours requirement',
    citation: '26 U.S.C. 45(b)(8)(A)',
    description: '0.3 of 3 hours is exactly 10% and compliant at a 10% threshold (float regression)',
    tags: ['boundary', 'regression', 'float-safety'],
  },
  {
    id: 'AP-004',
    area: 'apprenticeship',
    rule: 'Input integrity: apprentice hours cannot exceed total labor hours',
    citation: '26 U.S.C. 45(b)(8)(A)',
    description: 'Apprentice hours above total hours are rejected instead of passing',
    tags: ['failure-mode', 'input-validation'],
  },
  {
    id: 'AP-005',
    area: 'apprenticeship',
    rule: 'Input integrity: negative labor hours are rejected',
    citation: '26 U.S.C. 45(b)(8)(A)',
    description: 'Negative apprentice hours are rejected instead of producing a verdict',
    tags: ['failure-mode', 'input-validation'],
  },
  {
    id: 'AP-006',
    area: 'apprenticeship',
    rule: 'Input integrity: total labor hours must be positive',
    citation: '26 U.S.C. 45(b)(8)(A)',
    description: 'Zero total hours are rejected instead of causing division by zero',
    tags: ['failure-mode', 'input-validation'],
  },
  {
    id: 'PW-006',
    area: 'prevailing-wage',
    rule: 'Input integrity: sub-cent pay is rejected, not rounded',
    citation: '29 CFR 5.5(a)(1)(i)',
    description: 'A $44.995 rate is rejected instead of rounding up to $45.00 and passing',
    tags: ['failure-mode', 'input-validation', 'regression', 'money-impact'],
  },
];

export function scenariosFor(area: TestScenario['area']): TestScenario[] {
  return scenarioRegistry.filter((s) => s.area === area);
}
