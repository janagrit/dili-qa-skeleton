#!/bin/sh
# Judge for ts-fringe-support: hidden fringe tests + existing suite + types.
set -e
cp "$EVAL_DIR/checks/fringe.hidden.spec.ts" tests/
npm run --silent typecheck
npm test --silent
