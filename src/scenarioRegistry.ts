/**
 * Scenario registry: the executable specification of the compliance engine.
 *
 * Every rule from the source regulation becomes a cited, deterministic test
 * scenario. An auditor can follow any test failure back to the rule it
 * violates: scenario id -> rule -> citation.
 */

export interface TestScenario {
  id: string;
  area: 'prevailing-wage' | 'apprenticeship';
  rule: string;
  /** Real regulation citation. Rates and thresholds in tests are illustrative. */
  citation: string;
  description: string;
  tags: string[];
}

export const scenarioRegistry: TestScenario[] = [
  {
    id: 'PW-001',
    area: 'prevailing-wage',
    rule: 'Davis-Bacon Act',
    citation: '40 U.S.C. §§ 3141-3148; 29 CFR Part 5',
    description: 'Worker paid exactly the prevailing rate is compliant',
    tags: ['happy-path'],
  },
  {
    id: 'PW-002',
    area: 'prevailing-wage',
    rule: 'Davis-Bacon Act',
    citation: '40 U.S.C. §§ 3141-3148; 29 CFR Part 5',
    description: 'Worker paid below the prevailing rate is non-compliant with a computed shortfall',
    tags: ['violation', 'money-impact'],
  },
  {
    id: 'PW-003',
    area: 'prevailing-wage',
    rule: 'Davis-Bacon Act',
    citation: '40 U.S.C. §§ 3141-3148; 29 CFR Part 5',
    description: 'Worker paid above the prevailing rate is compliant',
    tags: ['boundary'],
  },
  {
    id: 'PW-004',
    area: 'prevailing-wage',
    rule: 'Davis-Bacon Act',
    citation: '29 CFR Part 5',
    description: 'Unknown worker classification fails loudly instead of silently passing',
    tags: ['failure-mode'],
  },
  {
    id: 'AP-001',
    area: 'apprenticeship',
    rule: 'IRA prevailing wage & apprenticeship requirements',
    citation: '26 U.S.C. § 45(b)(8)',
    description: 'Apprentice-hours ratio at the required threshold is compliant',
    tags: ['happy-path'],
  },
  {
    id: 'AP-002',
    area: 'apprenticeship',
    rule: 'IRA prevailing wage & apprenticeship requirements',
    citation: '26 U.S.C. § 45(b)(8)',
    description: 'Apprentice-hours ratio below the required threshold is non-compliant',
    tags: ['violation', 'money-impact'],
  },
];

export function scenariosFor(area: TestScenario['area']): TestScenario[] {
  return scenarioRegistry.filter((s) => s.area === area);
}
