import pytest
import re
from playwright.sync_api import Page, expect

from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage

class TestBookingScenario:
    """Full booking search scenario test class."""

    def test_booking_search_flow(self, page: Page) -> None:
        page.set_default_timeout(90_000)
        
        # مقادیر دقیق بر اساس نیازمندی
        FLEXIBLE_MONTH = "July 2026"
        TARGET_CURRENCY = "TRY"
        DESTINATION = "London"
        ADULTS = 8
        THIRD_HOTEL = 3

        home = HomePage(page)
        results = SearchResultsPage(page)

        home.open()

        home.click_currency_button()
        home.select_currency(TARGET_CURRENCY)

        home.fill_destination(DESTINATION)
        home.select_first_autocomplete_suggestion(DESTINATION)

        # مدیریت تقویم و انتخاب A month قبل از ماه
        home.open_date_picker()
        home.click_flexible_dates()
        home.select_a_month_duration()
        home.select_month(FLEXIBLE_MONTH)
        home.click_select_dates()

        home.open_occupancy_picker()
        home.set_adults_count(ADULTS)
        home.enable_travelling_with_pets()
        home.click_done()

        home.click_search()

        results.wait_for_results()
        
        with page.context.expect_page() as new_page_info:
            results.click_nth_hotel_availability(index=THIRD_HOTEL)
        
        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded")

        expect(new_page).to_have_url(re.compile(r"hotel"))
        assert "booking.com" in new_page.url, "Should be on a Booking.com hotel page"