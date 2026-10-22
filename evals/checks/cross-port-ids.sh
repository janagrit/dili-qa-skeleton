#!/bin/sh
# Judge for cross-port-id-check: both suites pass as-is, then fail once a TS
# scenario ID is renamed to one Python doesn't have. The rename covers the
# registry and its test case label, so the existing TS tests can't catch it.
set -e
npm test --silent
(cd python && "$EVAL_PYTEST" -q)
sed -i '' 's/PW-008/PW-099/g' src/scenarioRegistry.ts tests/prevailing-wage.spec.ts
grep -q "PW-099" src/scenarioRegistry.ts
if npm test --silent && (cd python && "$EVAL_PYTEST" -q); then
  echo "drifted ID PW-099 was not caught" >&2
  exit 1
fi
