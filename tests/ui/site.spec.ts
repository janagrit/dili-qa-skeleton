import { test, expect } from '../fixtures';

/**
 * Live-site smoke tests for www.dili.com (BASE_URL). They belong to the `ui`
 * project, so CI never runs them: `npm run test:ui`.
 *
 * Known production bugs are written as `test.fail(...)`: each test asserts the
 * CORRECT behaviour and is expected to fail while the bug exists. The run stays
 * green, the report lists them as "expected to fail", and once Dili fixes a bug
 * that test fails loudly so the marker gets removed. Bugs found 2026-10-17/18.
 */

const PAGES = ['/', '/about/', '/careers/', '/case-studies/', '/privacy/', '/terms/'];

test.describe('site health', () => {
  for (const path of PAGES) {
    test(`${path} loads with a title and footer`, async ({ page, sitePage }) => {
      const response = await sitePage.goto(path);
      expect(response?.status(), `${path} HTTP status`).toBe(200);
      await expect(page).toHaveTitle(/Dili/);
      await expect(sitePage.footer).toBeVisible();
    });
  }

  test('home page has no broken images', async ({ sitePage }) => {
    await sitePage.gotoAndSettle('/');
    expect(await sitePage.brokenImages()).toEqual([]);
  });
});

test.describe('known production bugs', () => {
  // BUG-1: the careers page loads jobs from /api/jobs, which returns
  // 502 {"error":"Dover API error"}, so no openings are listed.
  test.fail('BUG-1: /api/jobs returns job listings', async ({ request }) => {
    const response = await request.get('/api/jobs');
    expect(response.status(), await response.text()).toBe(200);
  });

  test.fail('BUG-1: careers page shows no server errors while loading jobs', async ({ sitePage }) => {
    const serverErrors = sitePage.recordServerErrors();
    await sitePage.gotoAndSettle('/careers/');
    expect(serverErrors).toEqual([]);
  });

  // BUG-2: /landing/ serves raw XML (application/xml) instead of an HTML page.
  test.fail('BUG-2: /landing/ serves an HTML page', async ({ request }) => {
    const response = await request.get('/landing/');
    expect(response.headers()['content-type']).toContain('text/html');
  });

  // BUG-3: some content is wider than a 390px phone. On a real phone the
  // browser then widens the page (410-421px measured) and shrinks everything
  // to fit; in a narrow desktop window it scrolls sideways instead (16-30px).
  // Measured 2026-10-18. Width = the wider of the layout viewport and content.
  test.describe('mobile layout', () => {
    const PHONE_WIDTH = 390;
    test.use({ viewport: { width: PHONE_WIDTH, height: 844 }, isMobile: true });

    for (const path of ['/', '/privacy/', '/landing/ira-landing/']) {
      test.fail(`BUG-3: ${path} fits a ${PHONE_WIDTH}px phone screen`, async ({ sitePage }) => {
        await sitePage.gotoAndSettle(path);
        const width = await sitePage.renderedWidth();
        expect(width, `${path} renders ${width}px wide on a ${PHONE_WIDTH}px screen`).toBe(
          PHONE_WIDTH,
        );
      });
    }

    test(`/about/ fits a ${PHONE_WIDTH}px phone screen (control)`, async ({ sitePage }) => {
      await sitePage.gotoAndSettle('/about/');
      expect(await sitePage.renderedWidth()).toBe(PHONE_WIDTH);
    });
  });

  // BUG-4 (empty login form gives no feedback) lives in login.spec.ts.
});
