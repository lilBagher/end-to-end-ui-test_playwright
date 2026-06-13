import re
from playwright.sync_api import Page
from .base_page import BasePage


class HomePage(BasePage):
    """Page Object Model for the Booking.com home page search form.

    Encapsulates all interactions with the main search form:
    currency picker, destination field, date picker,
    occupancy configuration, and the search button.
    """

    URL = "https://www.booking.com/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ─── Locators ───────────────────────────────────────────────────────────

    @property
    def currency_button(self):
        """Header currency picker trigger (e.g. 'GBP' button)."""
        return self.page.locator("[data-testid='header-currency-picker-trigger']")

    @property
    def destination_input(self):
        """'Where are you going?' text field."""
        return self.page.locator(
            "[data-testid='destination-container'] input, "
            "input[placeholder*='going'], "
            "input[name='ss']"
        ).first

    @property
    def date_picker_container(self):
        """Clickable date range area on the search form."""
        return self.page.locator("[data-testid='searchbox-dates-container']")

    @property
    def flexible_dates_tab(self):
        """'I'm flexible' tab inside the date picker."""
        return self.page.get_by_role(
            "tab", name=re.compile(r"flexible", re.IGNORECASE)
        ).first

    @property
    def a_month_button(self):
        """'A month' duration option inside the flexible date picker."""
        return self.page.get_by_role(
            "button", name=re.compile(r"^A month$", re.IGNORECASE)
        )

    @property
    def select_dates_button(self):
        """'Select dates' confirmation button in the date picker."""
        return self.page.get_by_role(
            "button", name=re.compile(r"Select dates", re.IGNORECASE)
        )

    @property
    def occupancy_config(self):
        """Guests / rooms configuration button on the search bar."""
        return self.page.locator("[data-testid='occupancy-config']")

    @property
    def adults_increment_btn(self):
        """'+' button to increase the adults count in the occupancy popup."""
        return self.page.locator(
            "[data-testid='occupancy-popup-adults-increment-button'], "
            "button[aria-label='Increase number of Adults']"
        ).first

    @property
    def adults_value_element(self):
        """Element showing the current number of adults."""
        return self.page.locator(
            "[data-testid='occupancy-popup-adults-value'], "
            "[data-testid='adults'] .c-stepper__value"
        ).first

    @property
    def pets_toggle(self):
        """'Travelling with pets?' checkbox / toggle."""
        return self.page.get_by_label(
            re.compile(r"Travelling with pets", re.IGNORECASE)
        )

    @property
    def done_button(self):
        """'Done' button that closes the occupancy popup."""
        return self.page.get_by_role("button", name="Done")

    @property
    def search_button(self):
        """Main 'Search' button that submits the form."""
        return self.page.locator("[data-testid='searchbox-submit-button']")

    # ─── Actions ────────────────────────────────────────────────────────────

    def open(self) -> None:
        """Open Booking.com and handle the cookie consent banner."""
        self.navigate_to(self.URL)
        self._accept_cookie_consent()

    def _accept_cookie_consent(self) -> None:
        """Click 'Accept' on the cookie banner if it appears."""
        try:
            btn = self.page.get_by_role(
                "button", name=re.compile(r"accept", re.IGNORECASE)
            ).first
            if btn.is_visible(timeout=4_000):
                btn.click()
        except Exception:
            pass  # Banner was not present

    # --- Currency -------------------------------------------------------

    def click_currency_button(self) -> None:
        """Open the currency picker dialog."""
        self.currency_button.wait_for(state="visible", timeout=10_000)
        self.currency_button.click()

    def select_currency(self, currency_code: str) -> None:
        """Choose a currency from the dialog by its code (e.g. 'TRY').

        Args:
            currency_code: Three-letter ISO currency code shown in the dialog.
        """
        self.page.wait_for_selector(
            f"text={currency_code}", state="visible", timeout=10_000
        )
        try:
            self.page.locator(
                f"[data-testid='selection-item']:has-text('{currency_code}')"
            ).first.click()
        except Exception:
            # Fallback: find any element whose text exactly matches the code
            self.page.get_by_text(currency_code, exact=True).first.click()

    # --- Destination ---------------------------------------------------

    def fill_destination(self, destination: str) -> None:
        """Type a destination into the search field.

        Args:
            destination: Free-text destination (e.g. 'London').
        """
        self.destination_input.wait_for(state="visible", timeout=10_000)
        self.destination_input.click()
        self.destination_input.fill(destination)

    def select_first_autocomplete_suggestion(self) -> None:
        """Wait for the autocomplete dropdown and click the first result."""
        first_result = self.page.locator(
            "[data-testid='autocomplete-result'], "
            "li[data-testid='autocomplete-result']"
        ).first
        first_result.wait_for(state="visible", timeout=10_000)
        first_result.click()

    # --- Dates ---------------------------------------------------------

    def open_date_picker(self) -> None:
        """Click on the date range area to open the date picker."""
        self.date_picker_container.click()

    def click_flexible_dates(self) -> None:
        """Switch the date picker to the 'I'm flexible' mode."""
        self.flexible_dates_tab.wait_for(state="visible", timeout=10_000)
        self.flexible_dates_tab.click()

    def select_a_month_duration(self) -> None:
        """Pick 'A month' as the trip duration under flexible dates."""
        self.a_month_button.wait_for(state="visible", timeout=10_000)
        self.a_month_button.click()

    def select_month(self, month_year: str) -> None:
        """Click a specific month in the flexible month selector.

        Args:
            month_year: Month and year label as shown on the button,
                        e.g. 'Jun 2025' or 'June 2025'.

        Note:
            Booking.com only shows future months. If the specified month
            is in the past, update this value to an upcoming month.
        """
        self.page.get_by_role(
            "button", name=re.compile(month_year, re.IGNORECASE)
        ).click()

    def click_select_dates(self) -> None:
        """Click 'Select dates' to confirm the date selection."""
        self.select_dates_button.wait_for(state="visible", timeout=10_000)
        self.select_dates_button.click()

    # --- Occupancy (Guests) --------------------------------------------

    def open_occupancy_picker(self) -> None:
        """Open the guests / rooms configuration popup."""
        self.occupancy_config.wait_for(state="visible", timeout=10_000)
        self.occupancy_config.click()

    def set_adults_count(self, target_count: int) -> None:
        """Increase the number of adults to the desired value.

        Args:
            target_count: Desired number of adults (e.g. 8).
                          Default on booking.com is 2.
        """
        current_text = self.adults_value_element.text_content(timeout=5_000)
        current = int(current_text.strip())
        for _ in range(target_count - current):
            self.adults_increment_btn.click()
            self.page.wait_for_timeout(300)

    def enable_travelling_with_pets(self) -> None:
        """Enable the 'Travelling with pets?' option."""
        self.pets_toggle.wait_for(state="visible", timeout=10_000)
        if not self.pets_toggle.is_checked():
            self.pets_toggle.click()

    def click_done(self) -> None:
        """Close the occupancy popup."""
        self.done_button.wait_for(state="visible", timeout=5_000)
        self.done_button.click()

    # --- Search --------------------------------------------------------

    def click_search(self) -> None:
        """Submit the search form."""
        self.search_button.wait_for(state="visible", timeout=10_000)
        self.search_button.click()
