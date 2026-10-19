# Dili QA

QA checks of Dili's live site and login, plus a compliance-scenario test suite
(Playwright + TypeScript, and Python).

## Findings

**See [FINDINGS.md](FINDINGS.md)** for the open issues found in Dili's product,
with expected behaviour for each.

## Run the tests

```bash
npm install
npx playwright install chromium
npm run test:ui     # live-site checks; known bugs show as "Known bug"
npm test            # compliance-scenario tests (no network)

cd python && pip install -r requirements-test.txt && pytest -q
```

Rates and rules in the compliance examples are illustrative, not legal advice.
