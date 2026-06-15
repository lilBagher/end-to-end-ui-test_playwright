"""
Base Page Object برای تمام صفحات.

متدها:
  - dismiss_popups()       : بستن خودکار popup‌های cookie/modal/sign-in
  - safe_click()           : کلیک با retry + popup guard
  - safe_fill()            : تایپ با retry + popup guard
  - navigate_to()          : Navigate با retry
  - take_screenshot()      : اسکرین‌شات برای Debug
  - wait_for_selector_visible() : انتظار برای visibility عنصر
"""

import os
import time
import logging

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError

from utils.retry import retry

logger = logging.getLogger(__name__)

# Selector های رایج popup ها (در subclass override کن)
GENERIC_POPUP_SELECTORS: list[str] = [
    # Cookie banners
    "#onetrust-accept-btn-handler",
    "button[data-testid='cookie-banner-accept-button']",
    "button:has-text('Accept all')",
    "button:has-text('Accept All')",
    "button:has-text('Accept')",
    "[id*='cookie'] button",
    "[class*='cookie-accept']",
    # Sign-in / Genius popups (Booking.com)
    "button[aria-label='Dismiss sign in information.']",
    "button[aria-label='Dismiss sign-in info.']",
    "[data-testid='modal-close-button']",
    ".bui-modal__close",
    # Generic modals
    "button[aria-label='Close']",
    "button:has-text('Not now')",
    "button:has-text('Skip')",
    "button:has-text('Close')",
]


class BasePage:
    """Base Page Object — تعامل رایج برای تمام صفحات."""

    DEFAULT_TIMEOUT = 60_000  # 60 ثانیه برای اتصالات ضعیف
    POPUP_TIMEOUT = 4_000     # 4 ثانیه برای چک کردن هر popup
    POPUP_SELECTORS = GENERIC_POPUP_SELECTORS  # در subclass override کن

    def __init__(self, page: Page) -> None:
        self.page = page
        self.page.set_default_timeout(self.DEFAULT_TIMEOUT)
        self.page.set_default_navigation_timeout(self.DEFAULT_TIMEOUT)

    # مدیریت Popup ها
    def dismiss_popups(self) -> int:
        """تمام popup های شناخته‌شده را ببند. هیچ Exception نمی‌دهد."""
        closed = 0
        for selector in self.POPUP_SELECTORS:
            try:
                btn = self.page.locator(selector).first
                btn.wait_for(state="visible", timeout=self.POPUP_TIMEOUT)
                btn.click(force=True)
                self.page.wait_for_timeout(400)  # منتظر تمام شدن انیمیشن
                logger.info(f"[Popup closed] {selector}")
                closed += 1
            except (PlaywrightTimeoutError, PlaywrightError):
                pass  # این popup موجود نبود
        return closed

    # Navigation
    @retry(max_attempts=3, delay=3.0)
    def navigate_to(self, url: str) -> None:
        """Navigate به URL با retry. بعد از لود، popup ها را ببند."""
        logger.info(f"[Navigate] {url}")
        self.page.goto(url, wait_until="domcontentloaded", timeout=self.DEFAULT_TIMEOUT)
        self.dismiss_popups()

    # اقدامات Safe (امن)
    @retry(max_attempts=3, delay=1.5)
    def safe_click(self, selector: str, timeout: int = None) -> None:
        """کلیک با retry. قبل از کلیک popup ها بررسی می‌شوند."""
        self.dismiss_popups()
        logger.debug(f"[Click] {selector}")
        self.page.locator(selector).click(
            force=True,
            timeout=timeout or self.DEFAULT_TIMEOUT,
        )

    @retry(max_attempts=3, delay=1.5)
    def safe_fill(self, selector: str, value: str, timeout: int = None) -> None:
        """پر کردن input با retry. فیلد را قبلاً پاک می‌کند."""
        self.dismiss_popups()
        logger.debug(f"[Fill] {selector} = '{value}'")
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout or self.DEFAULT_TIMEOUT)
        locator.clear()
        locator.fill(value)

    # Utilities (ابزارهای کمکی)
    def wait_for_selector_visible(self, selector: str, timeout: int = None):
        """منتظر بمان تا element مرئی شود و locator آن را برگردان."""
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout or self.DEFAULT_TIMEOUT)
        return locator

    def take_screenshot(self, filename: str) -> None:
        """اسکرین‌شات برای Debug (پوشه screenshots خودکار ساخته می‌شود)."""
        os.makedirs("screenshots", exist_ok=True)
        path = f"screenshots/{filename}_{int(time.time())}.png"
        self.page.screenshot(path=path, full_page=True)
        logger.info(f"[Screenshot] {path}")
