import { test, expect } from '@playwright/test';
import { scenarioRegistry } from '../src/scenarioRegistry';

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
