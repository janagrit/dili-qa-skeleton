#!/bin/sh
# Judge for login-no-fixed-wait. Runs the agent's empty-submit test against a
# local mock of the login page: it must pass when no login request is sent,
# and fail when one is sent at once or 250ms later (the old 1s sleep caught both).
set -e
if grep -q 'waitForTimeout' tests/login.spec.ts; then exit 1; fi
npm run --silent typecheck

PORT=${EVAL_MOCK_PORT:-4789}
run_against() {
  node "$EVAL_DIR/checks/mock-login-server.js" "$1" "$PORT" &
  pid=$!
  sleep 1
  status=0
  BASE_URL="http://127.0.0.1:$PORT" npx playwright test --project=ui \
    tests/login.spec.ts -g 'does not sign the user in' --retries=0 >/dev/null 2>&1 || status=$?
  kill "$pid"
  return "$status"
}

run_against good || { echo "fails against a page that sends nothing" >&2; exit 1; }
if run_against bad-now; then echo "missed an immediate login POST" >&2; exit 1; fi
if run_against bad-late; then echo "missed a login POST sent 250ms later" >&2; exit 1; fi
