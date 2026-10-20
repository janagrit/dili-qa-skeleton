# Dili QA Findings

**Date:** 2026-10-19
**Scope:** live checks of `www.dili.com` and the login flow at
`pwa.dili.ai/v2/login`, run with Playwright (desktop and a 390px phone viewport)
and direct HTTP requests.
**Status:** all five findings below are open in production.

Each finding (except the security issue) has an automated test in this repo
written as `test.fail(...)`: it asserts the correct behaviour and is expected to
fail while the bug exists. When a fix ships, the test passes, which shows the
fix is in. Run them with `npm run test:ui`.

---

## Summary

| # | Finding | Area | Severity | Test |
|---|---------|------|----------|------|
| 1 | Login API security issue | Auth API | Critical | — (details withheld) |
| 2 | Careers page shows no jobs: `/api/jobs` returns 502 | Careers | High | `site.spec.ts` BUG-1 |
| 3 | `/landing/` serves raw XML instead of a web page | Marketing site | Medium | `site.spec.ts` BUG-2 |
| 4 | Pages are wider than a phone screen | Mobile layout | Medium | `site.spec.ts` BUG-3 |
| 5 | Empty login form gives no validation message | Login UI | Medium | `login.spec.ts` BUG-4 |

---

## 1. Login API security issue — Critical

A possible authentication weakness in the login API was found during the live
check. Because it is a security issue, the details are not published in this
public repository.

- Shared with Dili for confirmation against the backend.
- No token or session was used or probed further.
- A regression test will be added once the intended behaviour is confirmed.

## 2. Careers page shows no jobs — High

The careers page loads its listings from `/api/jobs`, which returns
**HTTP 502** with `{"error":"Dover API error"}`. The page shows no open roles,
so candidates can't see or apply for jobs from the site. Re-checked 2026-10-19.

**Expected:** `/api/jobs` returns 200 with the job list, and the careers page
shows open roles. If the upstream job board is down, the page should show a
fallback message or a link instead of an empty list.

## 3. `/landing/` serves raw XML — Medium

`https://www.dili.com/landing/` responds with `Content-Type: application/xml`,
so browsers show raw XML instead of a page.

**Expected:** an HTML page (`text/html`), or a redirect to the correct landing
page.

## 4. Pages wider than a phone screen — Medium

On a 390px-wide phone viewport, `/`, `/privacy/` and `/landing/ira-landing/`
have content wider than the screen. On a phone the page renders at about
410–421px, so it zooms out or scrolls sideways; on a narrow desktop window it
scrolls 16–30px horizontally. `/about/` fits correctly and is used as the
control in the test.

**Expected:** no horizontal overflow at common phone widths (390px).

## 5. Empty login form gives no feedback — Medium

At `pwa.dili.ai/v2/login`, clicking **Sign in** with both fields empty does
nothing visible: no validation message, no login request, and the user stays
on the page. The inputs are not marked `required` and there is no client-side
validation.

**Expected:** a clear message such as "Email is required" next to each empty
field.

---

## How to reproduce

```bash
npm install
npx playwright install chromium
npm run test:ui
```

The run ends with a summary table. Findings 2–5 show as **Known bug**
(expected failures); when one is fixed, its row turns to **Failed**
("expected to fail, but passed"), which signals the fix is live.
