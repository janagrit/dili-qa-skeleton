import type { Locator, Page } from '@playwright/test';
import { LoginPage } from './LoginPage';

/** Marketing site home page (BASE_URL). */
export class HomePage {
  readonly logInLink: Locator;

  constructor(readonly page: Page) {
    this.logInLink = page.getByRole('navigation').getByRole('link', { name: 'Log In' });
  }

  async goto() {
    await this.page.goto('/');
  }

  /** Follows the nav "Log In" link and returns the PWA app sign-in page once it shows. */
  async openLogin(): Promise<LoginPage> {
    await this.logInLink.click();
    const loginPage = new LoginPage(this.page);
    await loginPage.expectLoaded();
    return loginPage;
  }
}
