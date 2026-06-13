import re
from playwright.sync_api import Page
from .base_page import BasePage


class SearchResultsPage(BasePage):
    """Page Object Model for the Booking.com search results page.

    Handles interactions on the hotel listing page shown after
    the user submits the search form.
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ─── Locators ───────────────────────────────────────────────────────────

    @property
    def hotel_cards(self):
        """All property / hotel cards visible on the results page."""
        return self.page.locator("[data-testid='property-card']")

    @property
    def see_availability_buttons(self):
        """All 'See availability' CTA links on the listing page."""
        return self.page.locator(
            "[data-testid='availability-cta-btn'], "
            "a[data-testid='availability-cta-btn']"
        )

    # ─── Actions ────────────────────────────────────────────────────────────

    def wait_for_results(self, timeout: int = 30_000) -> None:
        """Block until at least one hotel card is visible."""
        self.page.wait_for_load_state("networkidle", timeout=timeout)
        self.hotel_cards.first.wait_for(state="visible", timeout=timeout)

    def close_popup_if_visible(self) -> None:
        """Dismiss the Genius / sign-in popup shown over the results.

        The spec states: 'If you encounter this page, close it.'
        """
        close_selectors = [
            "button[aria-label='Dismiss sign in info.']",
            "button[aria-label='Close']",
            "[data-testid='modal-close-button']",
            "button:has-text('Close')",
        ]
        for selector in close_selectors:
            try:
                btn = self.page.locator(selector).first
                if btn.is_visible(timeout=2_000):
                    btn.click()
                    self.page.wait_for_timeout(500)
                    return
            except Exception:
                continue

    def click_nth_hotel_availability(self, index: int = 3) -> None:
        """Click 'See availability' for the hotel at the given 1-based position.

        Args:
            index: 1-based position of the hotel in the list (default 3 = 3rd hotel).
        """
        self.close_popup_if_visible()
        self.page.wait_for_timeout(800)

        btn = self.see_availability_buttons.nth(index - 1)
        btn.wait_for(state="visible", timeout=15_000)
        btn.scroll_into_view_if_needed()
        btn.click()
