import { test, expect } from '../fixtures';
import { LoginPage } from '../pages/LoginPage';

/**
 * UI login flow: marketing site (BASE_URL) -> "Log In" -> PWA app sign-in.
 * The valid-login test needs DILI_EMAIL / DILI_PASSWORD and is skipped without them.
 */
test.describe('login', () => {
  test('home page "Log In" opens the sign-in form', async ({ homePage }) => {
    await homePage.goto();
    const loginPage = await homePage.openLogin();
    await expect(loginPage.email).toBeVisible();
    await expect(loginPage.password).toBeVisible();
    await expect(loginPage.forgotPassword).toBeVisible();
    await expect(loginPage.ssoLink).toBeVisible();
  });

  test('invalid credentials show an error and stay on sign-in', async ({ page, homePage }) => {
    await homePage.goto();
    const loginPage = await homePage.openLogin();
    await loginPage.signIn('qa-invalid-user@example.com', 'not-a-real-password');
    await expect(loginPage.invalidCredentialsError).toBeVisible();
    await expect(page).toHaveURL(LoginPage.url);
  });

  test('empty form submit does not sign the user in', async ({ page, homePage }) => {
    await homePage.goto();
    const loginPage = await homePage.openLogin();

    // Track whether the app ever fires the login request on an empty submit.
    let loginAttempted = false;
    page.on('request', (req) => {
      if (LoginPage.isLoginRequest(req)) {
        loginAttempted = true;
      }
    });

    await loginPage.submit.click();
    await page.waitForTimeout(1000);

    // The core guarantee: a blank submit must never leave the sign-in page.
    await expect(page).toHaveURL(LoginPage.url);
    expect(loginAttempted, 'empty form should not call the login API').toBe(false);
  });

  // Known gap (2026-10-17): submitting the empty form gives no feedback at all —
  // the inputs are not `required` and there is no client-side validation message.
  // This asserts the intended behaviour, so it fails until that is fixed.
  test.fail('empty form submit shows a validation message', async ({ homePage }) => {
    await homePage.goto();
    const loginPage = await homePage.openLogin();
    await loginPage.submit.click();
    await expect(loginPage.validationMessage).toBeVisible();
  });

  test('valid credentials sign the user in', async ({ page, homePage }) => {
    const email = process.env.DILI_EMAIL;
    const password = process.env.DILI_PASSWORD;
    test.skip(!email || !password, 'set DILI_EMAIL and DILI_PASSWORD to run');

    await homePage.goto();
    const loginPage = await homePage.openLogin();
    await loginPage.signIn(email!, password!);
    await expect(page).not.toHaveURL(LoginPage.url);
    await expect(loginPage.invalidCredentialsError).toBeHidden();
  });
});
