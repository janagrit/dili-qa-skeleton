#!/bin/sh
# Judge for cross-port-id-check: both suites pass as-is, then fail once a TS
# scenario ID is renamed to one Python doesn't have. The rename covers the
# registry and its test case label, so the existing TS tests can't catch it.
set -e
# tests/logic/ is the current layout; the eval suite still runs on the old flat tests/.
SPEC=tests/logic/prevailing-wage.spec.ts
[ -f "$SPEC" ] || SPEC=tests/prevailing-wage.spec.ts
npm test --silent
(cd python && "$EVAL_PYTEST" -q)
# Undo the rename on exit, so running this by hand leaves the repo as it was.
cp src/scenarioRegistry.ts src/scenarioRegistry.ts.judge-bak
cp "$SPEC" "$SPEC.judge-bak"
trap 'mv src/scenarioRegistry.ts.judge-bak src/scenarioRegistry.ts; mv "$SPEC.judge-bak" "$SPEC"' EXIT
sed -i '' 's/PW-008/PW-099/g' src/scenarioRegistry.ts "$SPEC"
grep -q "PW-099" src/scenarioRegistry.ts
if npm test --silent && (cd python && "$EVAL_PYTEST" -q); then
  echo "drifted ID PW-099 was not caught" >&2
  exit 1
fi
