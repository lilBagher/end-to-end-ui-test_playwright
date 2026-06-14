import re
from playwright.sync_api import Page
from .base_page import BasePage

class SearchResultsPage(BasePage):
    """Page Object Model for the Booking.com search results page."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def hotel_cards(self):
        return self.page.locator("[data-testid='property-card']")

    @property
    def see_availability_buttons(self):
        return self.page.locator(
            "[data-testid='availability-cta-btn'], "
            "a[data-testid='availability-cta-btn']"
        )

    def wait_for_results(self, timeout: int = 90_000) -> None:
        self.hotel_cards.first.wait_for(state="visible", timeout=timeout)

    def close_popup_if_visible(self) -> None:
        close_selectors = [
            "button[aria-label='Dismiss sign in info.']",
            "button[aria-label='Close']",
            "[data-testid='modal-close-button']",
            "button:has-text('Close')",
        ]
        for selector in close_selectors:
            try:
                btn = self.page.locator(selector).first
                if btn.is_visible(timeout=4_000):
                    btn.click(force=True)
                    self.page.wait_for_timeout(1000)
                    return
            except Exception:
                continue

    def click_nth_hotel_availability(self, index: int = 3) -> None:
        self.close_popup_if_visible()
    
        # اول کارت هتل مورد نظر را پیدا می‌کند و صفحه را تا آنجا اسکرول می‌کند
        target_card = self.hotel_cards.nth(index - 1)
        target_card.wait_for(state="visible", timeout=30_000)
        target_card.scroll_into_view_if_needed()
        self.page.wait_for_timeout(1000) # اجازه می‌دهیم انیمیشن اسکرول تمام شود
        
        # سپس روی دکمه آن کلیک می‌کند
        btn = self.see_availability_buttons.nth(index - 1)
        btn.click(force=True)