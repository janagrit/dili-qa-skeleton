import { test, expect, type Page } from '@playwright/test';

/**
 * UI login flow: marketing site (BASE_URL) -> "Log In" -> PWA app sign-in.
 * The valid-login test needs DILI_EMAIL / DILI_PASSWORD and is skipped without them.
 */
async function openLoginFromHome(page: Page) {
  await page.goto('/');
  await page.getByRole('navigation').getByRole('link', { name: 'Log In' }).click();
  await expect(page).toHaveURL(/\/login/);
  await expect(page.getByRole('heading', { name: 'Sign in', level: 1 })).toBeVisible();
}

async function signIn(page: Page, email: string, password: string) {
  await page.getByRole('textbox', { name: 'Email' }).fill(email);
  await page.getByRole('textbox', { name: 'Password' }).fill(password);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
}

test.describe('login', () => {
  test('home page "Log In" opens the sign-in form', async ({ page }) => {
    await openLoginFromHome(page);
    await expect(page.getByRole('textbox', { name: 'Email' })).toBeVisible();
    await expect(page.getByRole('textbox', { name: 'Password' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Forgot password?' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Sign in with SSO' })).toBeVisible();
  });

  test('invalid credentials show an error and stay on sign-in', async ({ page }) => {
    await openLoginFromHome(page);
    await signIn(page, 'qa-invalid-user@example.com', 'not-a-real-password');
    await expect(page.getByText('Invalid username or password')).toBeVisible();
    await expect(page).toHaveURL(/\/login/);
  });

  test('empty form submit does not sign the user in', async ({ page }) => {
    await openLoginFromHome(page);

    // Track whether the app ever fires the login request on an empty submit.
    let loginAttempted = false;
    page.on('request', (req) => {
      if (req.method() === 'POST' && /\/auth\/login\/?$/.test(req.url())) {
        loginAttempted = true;
      }
    });

    await page.getByRole('button', { name: 'Sign in', exact: true }).click();
    await page.waitForTimeout(1000);

    // The core guarantee: a blank submit must never leave the sign-in page.
    await expect(page).toHaveURL(/\/login/);
    expect(loginAttempted, 'empty form should not call the login API').toBe(false);
  });

  // Known gap (2026-10-17): submitting the empty form gives no feedback at all —
  // the inputs are not `required` and there is no client-side validation message.
  // This asserts the intended behaviour, so it fails until that is fixed.
  test.fail('empty form submit shows a validation message', async ({ page }) => {
    await openLoginFromHome(page);
    await page.getByRole('button', { name: 'Sign in', exact: true }).click();
    await expect(
      page.getByText(/required|enter your email|enter your password/i),
    ).toBeVisible();
  });

  test('valid credentials sign the user in', async ({ page }) => {
    const email = process.env.DILI_EMAIL;
    const password = process.env.DILI_PASSWORD;
    test.skip(!email || !password, 'set DILI_EMAIL and DILI_PASSWORD to run');

    await openLoginFromHome(page);
    await signIn(page, email!, password!);
    await expect(page).not.toHaveURL(/\/login/);
    await expect(page.getByText('Invalid username or password')).toBeHidden();
  });
});
