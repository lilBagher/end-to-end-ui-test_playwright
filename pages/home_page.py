"""
Page Object برای صفحه اصلی Booking.com

تعاملات اصلی:
  - باز کردن صفحه و مدیریت popup ها
  - تغییر ارز
  - جستجو و انتخاب مقصد
  - انتخاب تاریخ (جستجوی انعطاف پذیر)
  - تنظیم تعداد مسافران و حیوانات خانگی
  - ارسال جستجو
"""

import re
import logging

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from .base_page import BasePage
from utils.retry import retry

logger = logging.getLogger(__name__)


class HomePage(BasePage):
    URL = "https://www.booking.com/"

    # Selector های اختصاصی Booking.com
    POPUP_SELECTORS = [
        "#onetrust-accept-btn-handler",
        "button[data-testid='cookie-banner-accept-button']",
        "button[aria-label='Dismiss sign in information.']",
        "button[aria-label='Dismiss sign-in info.']",
        "[data-testid='modal-close-button']",
        ".bui-modal__close",
        "button:has-text('Accept')",
        "button:has-text('Close')",
        "button:has-text('Not now')",
    ]

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # Locators
    @property
    def currency_button(self):
        return self.page.locator("[data-testid='header-currency-picker-trigger']")

    @property
    def destination_input(self):
        return self.page.locator(
            "[data-testid='destination-container'] input, "
            "input[placeholder*='going'], "
            "input[name='ss']"
        ).first

    @property
    def date_picker_container(self):
        return self.page.locator("[data-testid='searchbox-dates-container']")

    @property
    def flexible_dates_tab(self):
        return self.page.locator("button, [role='tab']").filter(
            has_text=re.compile(r"I'm flexible|Flexible", re.IGNORECASE)
        ).first

    @property
    def a_month_option(self):
        return self.page.locator("label").filter(
            has_text=re.compile(r"A month", re.IGNORECASE)
        ).first

    @property
    def select_dates_button(self):
        return self.page.locator("button").filter(
            has_text=re.compile(r"Select dates", re.IGNORECASE)
        ).first

    @property
    def occupancy_config(self):
        return self.page.locator(
            "[data-testid='occupancy-config'], "
            "button:has-text('adults'), "
            "button:has-text('Adults')"
        ).first
    
    @property
    def adults_increment_btn(self):
        return self.page.locator("input#group_adults").locator("..").locator("button").nth(1)

    @property
    def adults_value_element(self):
        return self.page.locator("input#group_adults")

    @property
    def pets_toggle(self):
        return self.page.locator("input#pets")

    @property
    def done_button(self):
        return self.page.get_by_role("button", name="Done")

    @property
    def search_button(self):
        return self.page.locator("button[type='submit']").first

    # باز کردن
    def open(self) -> None:
        """صفحه اصلی را باز کن و popup ها را ببند."""
        self.navigate_to(self.URL)

        # منتظر لود شدن فیلد جستجو
        self.destination_input.wait_for(state="visible", timeout=self.DEFAULT_TIMEOUT)

        self.dismiss_popups()
        # Escape برای بستن هر overlay احتمالی
        self.page.keyboard.press("Escape")
        self.dismiss_popups()
    # ارز
    @retry(max_attempts=3, delay=2.0)
    def click_currency_button(self) -> None:
        self.currency_button.wait_for(state="visible", timeout=15_000)
        self.currency_button.click()

    @retry(max_attempts=3, delay=2.0)
    def select_currency(self, currency_code: str) -> None:
        # منتظر ظاهر شدن لیست ارزها
        self.page.locator("[data-testid='selection-item']").first.wait_for(
            state="visible", timeout=15_000
        )
        try:
            btn = self.page.locator(
                f"[data-testid='selection-item']:has-text('{currency_code}')"
            ).first
            btn.scroll_into_view_if_needed()
            btn.click(force=True)
        except Exception:
            # Fallback اگر data-testid موجود نباشد
            fallback = self.page.locator(
                f"button:has-text('{currency_code}'), span:has-text('{currency_code}')"
            ).first
            fallback.scroll_into_view_if_needed()
            fallback.click(force=True)

    # مقصد
    @retry(max_attempts=3, delay=2.0)
    def search_and_select_destination(self, destination: str) -> None:
        """تایپ مقصد و انتخاب از پیشنهادات."""
        # پاک کردن فیلد (برای retry های مجدد)
        self.destination_input.wait_for(state="visible")
        self.destination_input.click(force=True)
        self.destination_input.clear()

        # تایپ با تاخیر برای فعال کردن autocomplete
        self.destination_input.press_sequentially(destination, delay=120)

        # منتظر ظاهر شدن پیشنهاد
        suggestion = self.page.locator(
            f"[data-testid='autocomplete-result']:has-text('{destination}')"
        ).first
        suggestion.wait_for(state="visible", timeout=15_000)

        # کلیک روی پیشنهاد
        suggestion.click(force=True)

        # منتظر بسته شدن پیشنهادات (تایید کردن ثبت کلیک)
        suggestion.wait_for(state="hidden", timeout=5_000)
    # تاریخ ها
    @retry(max_attempts=3, delay=2.0)
    def open_date_picker(self) -> None:
        if self.flexible_dates_tab.is_visible():
            return
        try:
            self.flexible_dates_tab.wait_for(state="visible", timeout=3_000)
        except PlaywrightTimeoutError:
            self.date_picker_container.click(force=True)
            self.flexible_dates_tab.wait_for(state="visible", timeout=10_000)

    @retry(max_attempts=3, delay=2.0)
    def click_flexible_dates(self) -> None:
        self.flexible_dates_tab.wait_for(state="visible", timeout=10_000)
        self.flexible_dates_tab.click(force=True)
        # منتظر ظاهر شدن گزینه های مدت زمان
        self.a_month_option.wait_for(state="visible", timeout=10_000)

    @retry(max_attempts=3, delay=2.0)
    def select_a_month_duration(self) -> None:
        try:
            self.a_month_option.wait_for(state="visible", timeout=8_000)
            self.a_month_option.click(force=True)
        except Exception:
            radio_btn = self.page.get_by_role(
                "radio", name=re.compile(r"A month", re.IGNORECASE)
            ).first
            radio_btn.wait_for(state="attached", timeout=5_000)
            radio_btn.check(force=True)

    @retry(max_attempts=3, delay=2.0)
    def select_month(self, month_year: str) -> None:
        parts = month_year.split()
        short_month = parts[0][:3]
        year = parts[-1]

        month_label = self.page.locator("[data-testid='flexible-dates-month']").filter(
            has_text=re.compile(f"{short_month}.*{year}", re.IGNORECASE)
        ).first

        try:
            month_label.wait_for(state="visible", timeout=10_000)
            month_label.scroll_into_view_if_needed()
            month_label.click(force=True)
        except Exception:
            fallback = self.page.locator(
                f"label:has-text('{short_month}'):has-text('{year}')"
            ).first
            fallback.scroll_into_view_if_needed()
            fallback.click(force=True)

    @retry(max_attempts=3, delay=1.5)
    def click_select_dates(self) -> None:
        self.select_dates_button.wait_for(state="visible", timeout=8_000)
        self.select_dates_button.click(force=True)

        # منتظر بسته شدن تقویم (دکمه ناپدید شود)
        self.select_dates_button.wait_for(state="hidden", timeout=5_000)
    # تعداد مسافران
    @retry(max_attempts=3, delay=1.5)
    def open_occupancy_picker(self) -> None:
        # Escape برای بستن منوی مقصد که خودکار باز می‌شود
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(500)  # مکث برای انیمیشن

        self.occupancy_config.wait_for(state="visible")
        self.occupancy_config.click(force=True)
        # منتظر باز شدن dropdown
        self.adults_value_element.wait_for(state="attached", timeout=8_000)
    @retry(max_attempts=3, delay=1.5)
    def set_adults_count(self, target_count: int) -> None:
        self.adults_value_element.wait_for(state="attached", timeout=8_000)
        current = int(self.adults_value_element.get_attribute("value"))

        while current < target_count:
            self.adults_increment_btn.click(force=True)
            # منتظر آپدیت شدن مقدار input
            self.page.wait_for_function(
                f"document.querySelector('input#group_adults').value > {current}",
                timeout=5_000,
            )
            current = int(self.adults_value_element.get_attribute("value"))

    @retry(max_attempts=3, delay=1.5)
    def enable_travelling_with_pets(self) -> None:
        pet_label = self.page.locator("label[for='pets']")
        pet_label.wait_for(state="visible", timeout=8_000)
        if not self.pets_toggle.is_checked():
            pet_label.click(force=True)

    @retry(max_attempts=3, delay=1.5)
    def click_done(self) -> None:
        self.done_button.wait_for(state="visible")
        self.done_button.click(force=True)
        # منتظر بسته شدن dropdown
        self.occupancy_config.wait_for(state="visible", timeout=8_000)

    # جستجو
    @retry(max_attempts=3, delay=2.0)
    def click_search(self) -> None:
        self.dismiss_popups()
        self.search_button.wait_for(state="visible")
        self.search_button.click(force=True)
