#!/bin/sh
# Judge for ts-fringe-support: hidden fringe tests + existing suite + types.
set -e
# tests/logic/ is the current layout (one level deeper, so the import gains a ../);
# the eval suite still runs on the old flat tests/.
if [ -d tests/logic ]; then
  HIDDEN=tests/logic/fringe.hidden.spec.ts
  sed "s#'../src/#'../../src/#" "$EVAL_DIR/checks/fringe.hidden.spec.ts" > "$HIDDEN"
else
  HIDDEN=tests/fringe.hidden.spec.ts
  cp "$EVAL_DIR/checks/fringe.hidden.spec.ts" "$HIDDEN"
fi
# Remove the hidden spec on exit, so running this by hand leaves the repo as it was.
trap 'rm -f "$HIDDEN"' EXIT
npm run --silent typecheck
npm test --silent
