import type { Locator, Page } from '@playwright/test';

/** Any page of the marketing site: what the site-health and layout checks need. */
export class SitePage {
  readonly footer: Locator;

  constructor(readonly page: Page) {
    this.footer = page.getByText(/© \d{4} Dili Inc/);
  }

  goto(path: string) {
    return this.page.goto(path);
  }

  /** Opens the page and waits for network quiet, so late images and API calls have landed. */
  async gotoAndSettle(path: string) {
    await this.page.goto(path);
    await this.page.waitForLoadState('networkidle');
  }

  /** Starts recording 5xx responses; the returned list fills in as the page loads. */
  recordServerErrors(): string[] {
    const serverErrors: string[] = [];
    this.page.on('response', (r) => {
      if (r.status() >= 500) serverErrors.push(`${r.status()} ${r.url()}`);
    });
    return serverErrors;
  }

  /** Sources of images that finished loading with no pixels. */
  brokenImages(): Promise<string[]> {
    return this.page.$$eval('img', (imgs) =>
      imgs.filter((i) => i.complete && i.naturalWidth === 0).map((i) => i.src),
    );
  }

  /** The wider of the layout viewport and the content. */
  renderedWidth(): Promise<number> {
    return this.page.evaluate(() =>
      Math.max(window.innerWidth, document.documentElement.scrollWidth),
    );
  }
}
