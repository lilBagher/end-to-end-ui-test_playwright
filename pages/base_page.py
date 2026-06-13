from playwright.sync_api import Page


class BasePage:
    """Base class for all Page Object Model classes.
    
    Provides common utility methods shared across all pages.
    """

    def __init__(self, page: Page) -> None:
        self.page = page

    def navigate_to(self, url: str) -> None:
        """Navigate to a URL and wait for the page to be ready."""
        self.page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        self.page.wait_for_load_state("networkidle", timeout=30_000)

    def take_screenshot(self, filename: str) -> None:
        """Save a screenshot for debugging purposes."""
        self.page.screenshot(path=f"screenshots/{filename}.png")

    def wait_for_selector_visible(self, selector: str, timeout: int = 10_000):
        """Wait until an element is visible and return its locator."""
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout)
        return locator
