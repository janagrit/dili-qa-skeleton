import { test as base } from '@playwright/test';
import { HomePage } from './pages/HomePage';
import { SitePage } from './pages/SitePage';

/**
 * UI specs import `test` from here to get page objects as fixtures.
 * There is no LoginPage fixture: `homePage.openLogin()` returns it once loaded.
 */
export const test = base.extend<{ homePage: HomePage; sitePage: SitePage }>({
  homePage: async ({ page }, use) => {
    await use(new HomePage(page));
  },
  sitePage: async ({ page }, use) => {
    await use(new SitePage(page));
  },
});

export { expect } from '@playwright/test';
