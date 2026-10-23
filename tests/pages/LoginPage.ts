import { expect, type Locator, type Page, type Request } from '@playwright/test';

/** PWA app sign-in page, reached from the home page "Log In" link. */
export class LoginPage {
  static readonly url = /\/login/;

  readonly heading: Locator;
  readonly email: Locator;
  readonly password: Locator;
  readonly submit: Locator;
  readonly forgotPassword: Locator;
  readonly ssoLink: Locator;
  readonly invalidCredentialsError: Locator;
  readonly validationMessage: Locator;

  constructor(readonly page: Page) {
    this.heading = page.getByRole('heading', { name: 'Sign in', level: 1 });
    this.email = page.getByRole('textbox', { name: 'Email' });
    this.password = page.getByRole('textbox', { name: 'Password' });
    this.submit = page.getByRole('button', { name: 'Sign in', exact: true });
    this.forgotPassword = page.getByRole('link', { name: 'Forgot password?' });
    this.ssoLink = page.getByRole('link', { name: 'Sign in with SSO' });
    this.invalidCredentialsError = page.getByText('Invalid username or password');
    this.validationMessage = page.getByText(/required|enter your email|enter your password/i);
  }

  /** The login API call the app makes when the form is submitted. */
  static isLoginRequest(req: Request) {
    return req.method() === 'POST' && /\/auth\/login\/?$/.test(req.url());
  }

  /** Waits until the sign-in form is showing. */
  async expectLoaded() {
    await expect(this.page).toHaveURL(LoginPage.url);
    await expect(this.heading).toBeVisible();
  }

  async signIn(email: string, password: string) {
    await this.email.fill(email);
    await this.password.fill(password);
    await this.submit.click();
  }
}
