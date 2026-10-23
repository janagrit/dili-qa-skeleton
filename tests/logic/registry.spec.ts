import { test, expect } from '@playwright/test';
import { scenarioRegistry } from '../../src/scenarioRegistry';

/**
 * Traceability meta-tests: the registry itself is under test.
 * An auditor must be able to follow any scenario back to its rule.
 */
test('every scenario has an id, a rule and a citation', async () => {
  for (const scenario of scenarioRegistry) {
    expect(scenario.id, 'scenario id').toBeTruthy();
    expect(scenario.rule, `rule for ${scenario.id}`).toBeTruthy();
    expect(scenario.citation, `citation for ${scenario.id}`).toBeTruthy();
    expect(scenario.description, `description for ${scenario.id}`).toBeTruthy();
  }
});

test('scenario ids are unique', async () => {
  const ids = scenarioRegistry.map((s) => s.id);
  expect(new Set(ids).size).toBe(ids.length);
});

// Citations a scenario may use. A well-formed but wrong paragraph must be added
// here deliberately, where a reviewer can check it (headings verified 2026-10-18).
const ALLOWED_CITATIONS = new Set([
  '29 CFR 5.5(a)(1)(i)', // wage rates and fringe benefits
  '29 CFR 5.5(a)(1)(iii)', // conformance (unlisted classifications)
  '26 U.S.C. 45(b)(8)(A)', // apprenticeship labor hours / applicable percentage
]);

test('citations are paragraph-level and on the reviewed list', async () => {
  for (const scenario of scenarioRegistry) {
    expect(scenario.citation, `${scenario.id} citation too broad`).not.toMatch(/Part \d+$|Part \d+;/);
    expect(ALLOWED_CITATIONS.has(scenario.citation), `${scenario.id}: ${scenario.citation}`).toBe(true);
  }
});
