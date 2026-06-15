import logging

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from .base_page import BasePage
from utils.retry import retry

logger = logging.getLogger(__name__)


class SearchResultsPage(BasePage):
    """Page Object برای صفحه نتایج جستجو."""

    POPUP_SELECTORS = [
        "button[aria-label='Dismiss sign in info.']",
        "button[aria-label='Dismiss sign in information.']",
        "[data-testid='modal-close-button']",
        "button:has-text('Close')",
        "button:has-text('Sign in')",
        "button:has-text('Not now')",
    ]

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def see_availability_buttons(self):
        # سلکتور ترکیبی مقاوم در برابر A/B Testing
        return self.page.locator(
            "a:has-text('See availability'), "
            "button:has-text('See availability'), "
            "a:has-text('See Availability'), "
            "button:has-text('See Availability'), "
            "[data-testid='availability-cta-btn']"
        )

    def wait_for_results(self, timeout: int = 60_000) -> None:
        """منتظر لود شدن اولین دکمه availability."""
        try:
            self.see_availability_buttons.first.wait_for(state="attached", timeout=timeout)
        except PlaywrightTimeoutError:
            # هیچ هتلی تطابق ندارد (مثلاً 8 مسافر در 1 اتاق)
            raise IndexError("صفحه نتایج لود شد اما هیچ هتلی با این معیارها پیدا نشد.")

        self.dismiss_popups()

    @retry(max_attempts=3, delay=2.0)
    def click_nth_hotel_availability(self, index: int = 3) -> None:
        """روی دکمه 'See availability' هتل n‌ام کلیک کن."""
        self.dismiss_popups()

        # اسکرول برای لود کردن نتایج بیشتر
        for _ in range(8):
            if self.see_availability_buttons.count() >= index:
                break
            self.page.keyboard.press("PageDown")
            self.page.wait_for_timeout(1000)

        available_count = self.see_availability_buttons.count()

        if available_count < index:
            raise IndexError(f"{available_count} هتل پیدا شد اما هتل #{index} درخواست شد.")

        btn = self.see_availability_buttons.nth(index - 1)

        # اسکرول به وسط صفحه با انیمیشن
        btn.evaluate("node => node.scrollIntoView({behavior: 'smooth', block: 'center'})")
        self.page.wait_for_timeout(1500)

        self.dismiss_popups()

        # کلیک نهایی
        btn.click(force=True)