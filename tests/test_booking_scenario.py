"""
End-to-end automation test for Booking.com
=========================================

Scenario (as defined in the Mohaymen technical evaluation):
    1. Open https://www.booking.com/
    2. Click the currency button and select TRY (Turkish Lira)
    3. Enter 'London' in the destination field and pick the first suggestion
    4. Open the date picker → switch to 'I'm flexible' → pick 'A month'
       → select 'Jun 2025' → click 'Select dates'
    5. Open the guests popup → set Adults = 8 → enable 'Travelling with pets?'
    6. Click Search
    7. On the results page, close any popup if visible
    8. Click 'See availability' for the 3rd hotel in the list

Pattern: Page Object Model (POM)
Tool:    Playwright via pytest-playwright
"""

import pytest
from playwright.sync_api import Page

from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage


class TestBookingScenario:
    """Full booking search scenario test class."""

    def test_booking_search_flow(self, page: Page) -> None:
        """
        Execute the complete Booking.com search scenario step by step.

        Note on the 'Jun 2025' month selection:
            Booking.com only displays future months in the flexible date picker.
            If the test is run after June 2025, update FLEXIBLE_MONTH to a
            future month (e.g. 'Jun 2026') or parameterize it via a fixture.
        """
        FLEXIBLE_MONTH = "Jun 2025"   # ← Update this if June 2025 has passed
        TARGET_CURRENCY = "TRY"
        DESTINATION = "London"
        ADULTS = 8
        THIRD_HOTEL = 3

        home = HomePage(page)
        results = SearchResultsPage(page)

        # ── Step 1: Open Booking.com ──────────────────────────────────────
        home.open()

        # ── Step 2: Change currency to TRY ───────────────────────────────
        home.click_currency_button()
        home.select_currency(TARGET_CURRENCY)

        # ── Step 3: Set destination to London ────────────────────────────
        home.fill_destination(DESTINATION)
        home.select_first_autocomplete_suggestion()

        # ── Step 4: Configure flexible dates ─────────────────────────────
        home.open_date_picker()
        home.click_flexible_dates()
        home.select_a_month_duration()
        home.select_month(FLEXIBLE_MONTH)
        home.click_select_dates()

        # ── Step 5: Configure occupancy ───────────────────────────────────
        home.open_occupancy_picker()
        home.set_adults_count(ADULTS)
        home.enable_travelling_with_pets()
        home.click_done()

        # ── Step 6: Search ────────────────────────────────────────────────
        home.click_search()

        # ── Step 7 & 8: Interact with results ────────────────────────────
        results.wait_for_results()
        results.click_nth_hotel_availability(index=THIRD_HOTEL)

        # Basic assertion: we should have navigated away from the home page
        page.wait_for_load_state("domcontentloaded")
        assert "booking.com" in page.url, "Should still be on a Booking.com page"
        assert page.url != "https://www.booking.com/", (
            "Should have navigated to a hotel detail page"
        )
