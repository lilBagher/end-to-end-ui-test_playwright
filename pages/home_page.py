import re
from playwright.sync_api import Page
from .base_page import BasePage

class HomePage(BasePage):
    URL = "https://www.booking.com/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ─── Locators ───────────────────────────────────────────────────────────
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
        """'A month' duration option (Radio button wrapper / label)."""
        # بهترین راه: پیدا کردن تگ لیبلی که شامل متن مورد نظر است
        return self.page.locator("label").filter(
            has_text=re.compile(r"A month", re.IGNORECASE)
        ).first

    @property
    def select_dates_button(self):
        """'Select dates' confirmation button."""
        return self.page.locator("button").filter(
            has_text=re.compile(r"Select dates", re.IGNORECASE)
        ).first

    @property
    def occupancy_config(self):
        return self.page.locator("[data-testid='occupancy-config']")

    @property
    def adults_increment_btn(self):
        """The '+' button for adults. Targets the exact parent of the hidden input."""
        # پیدا کردن اینپوت مسافران -> برگشت به والد مستقیم با ".." -> انتخاب دومین دکمه (+)
        return self.page.locator("input#group_adults").locator("..").locator("button").nth(1)

    @property
    def adults_value_element(self):
        """The hidden input containing the numeric count of adults."""
        return self.page.locator("input#group_adults")

    @property
    def pets_toggle(self):
        """The toggle/checkbox for traveling with pets."""
        # طبق کد ارسالی شما، id این چک‌باکس دقیقا "pets" است
        return self.page.locator("input#pets")

    @property
    def done_button(self):
        return self.page.get_by_role("button", name="Done")

    @property
    def search_button(self):
        return self.page.locator("button[type='submit']").first

    # ─── Actions ────────────────────────────────────────────────────────────
    def open(self) -> None:
        self.navigate_to(self.URL)
        self.page.wait_for_timeout(3000) 
        self._accept_cookie_consent()
        self._close_genius_popup()
        self.page.keyboard.press("Escape")

    def _accept_cookie_consent(self) -> None:
        try:
            btn = self.page.locator(
                "#onetrust-accept-btn-handler, "
                "button[data-testid='cookie-banner-accept-button'], "
                "button:has-text('Accept')"
            ).first
            btn.wait_for(state="visible", timeout=8000)
            btn.click(force=True)
            self.page.wait_for_timeout(1000)
        except Exception:
            pass 

    def _close_genius_popup(self) -> None:
        close_selectors = [
            "button[aria-label='Dismiss sign in information.']",
            "button[aria-label='Dismiss sign-in info.']",
            "button[aria-label='Close']",
            "[data-testid='modal-close-button']",
            ".bui-modal__close",
        ]
        for selector in close_selectors:
            try:
                btn = self.page.locator(selector).first
                btn.wait_for(state="visible", timeout=2000)
                btn.click(force=True)
                self.page.wait_for_timeout(500)
                return  
            except Exception:
                continue

    # --- Currency ---
    def click_currency_button(self) -> None:
        self.currency_button.wait_for(state="visible", timeout=10_000)
        self.currency_button.click()

    def select_currency(self, currency_code: str) -> None:
        # منتظر ماندن برای لود شدن کل مودال ارزها
        self.page.locator("[data-testid='selection-item']").first.wait_for(state="visible", timeout=10000)
        try:
            btn = self.page.locator(f"[data-testid='selection-item']:has-text('{currency_code}')").first
            btn.scroll_into_view_if_needed() # اسکرول کردن به سمت لیر (TRY)
            btn.click(force=True)
        except Exception:
            fallback = self.page.locator(f"button:has-text('{currency_code}'), span:has-text('{currency_code}')").first
            fallback.scroll_into_view_if_needed()
            fallback.click(force=True)

    # --- Destination ---
    def fill_destination(self, destination: str) -> None:
        """Type the destination safely by manually clearing the field first."""
        self.destination_input.wait_for(state="visible")
        self.destination_input.click(force=True)
        """
        ### پاک کردن مطمئن و واقعی فیلد با شبیه‌سازی کیبورد
        self.page.keyboard.press("Control+A")
        self.page.keyboard.press("Backspace")
        self.page.wait_for_timeout(500)
        """
        # تایپ کلمه جدید
        self.destination_input.press_sequentially(destination, delay=150)
        self.page.wait_for_timeout(2000)

    def select_first_autocomplete_suggestion(self, destination: str) -> None:
        """Type destination slowly and wait for accurate network response before clicking."""
        
        suggestion = self.page.locator(
            f"[data-testid='autocomplete-result']:has-text('{destination}')"
        ).first
        
  
        suggestion.wait_for(state="visible", timeout=10000)
        suggestion.click(force=True)
            
            # یک مکث کوتاه برای اینکه سایت متوجه کلیک شود و تقویم را باز کند
        self.page.wait_for_timeout(2000)
            
    # --- Dates ---
    def open_date_picker(self) -> None:
        # اگر تقویم خودکار باز شده، دیگر روی آن کلیک نکن
        if self.flexible_dates_tab.is_visible():
            return
        try:
            self.flexible_dates_tab.wait_for(state="visible", timeout=3000)
        except Exception:
            self.date_picker_container.click(force=True)
            self.flexible_dates_tab.wait_for(state="visible", timeout=5000)

    def click_flexible_dates(self) -> None:
        self.flexible_dates_tab.wait_for(state="visible", timeout=5000)
        self.flexible_dates_tab.click(force=True)

    def select_a_month_duration(self) -> None:
        """Select 'A month' duration option using label click or radio check."""
        try:
            # تلاش اول: کلیک روی لیبل گرافیکی متصل به رادیو باتن
            self.a_month_option.wait_for(state="visible", timeout=8000)
            self.a_month_option.click(force=True)
        except Exception:
            # روش جایگزین: پیدا کردن مستقیم خود رادیو باتن و استفاده از متد check()
            radio_btn = self.page.get_by_role("radio", name=re.compile(r"A month", re.IGNORECASE)).first
            # از state="attached" استفاده می‌کنیم چون ممکن است رادیو باتن در پس‌زمینه مخفی باشد
            radio_btn.wait_for(state="attached", timeout=5000)
            radio_btn.check(force=True)

    def select_month(self, month_year: str) -> None:
        """Select the specified month in the flexible dates view based on explicit DOM structure."""
        
        # استخراج هوشمندِ نام ماه و سال (تبدیل "July 2026" به "Jul" و "2026")
        parts = month_year.split()
        short_month = parts[0][:3]  # سه حرف اول ماه
        year = parts[-1]            # عدد سال
        
        # استفاده از data-testid خالصی که از HTML استخراج کردید
        # رجکس {short_month}.*{year} یعنی مثلا هرجا نوشت Jul بعدش هرچیزی بود بعدش 2026 بود
        month_label = self.page.locator("[data-testid='flexible-dates-month']").filter(
            has_text=re.compile(f"{short_month}.*{year}", re.IGNORECASE)
        ).first
        
        try:
            month_label.wait_for(state="visible", timeout=8000)
            month_label.scroll_into_view_if_needed()
            # چون تگ اینپوت (چک‌باکس) داخل لیبل پنهان است، کلیک کردن مستقیم روی لیبل امن‌ترین کار است
            month_label.click(force=True)
        except Exception:
            # روش جایگزین در صورت تغییرات احتمالی DOM
            fallback = self.page.locator(f"label:has-text('{short_month}'):has-text('{year}')").first
            fallback.scroll_into_view_if_needed()
            fallback.click(force=True)
            
    def click_select_dates(self) -> None:
       
            # حداکثر ۳ ثانیه منتظر می‌ماند
            self.select_dates_button.wait_for(state="visible", timeout=3000)
            self.select_dates_button.click(force=True)
            self.page.wait_for_timeout(500)

    # --- Occupancy ---
    def open_occupancy_picker(self) -> None:
        self.occupancy_config.wait_for(state="visible")
        self.occupancy_config.click(force=True)

    def set_adults_count(self, target_count: int) -> None:
        """Click the '+' button until the target adults count is reached."""
        # چون اینپوت مخفی (type="range") است، باید از attached به جای visible استفاده کنیم
        self.adults_value_element.wait_for(state="attached", timeout=5000)
        
        # خواندن مقدار عددی دقیق از اتریبیوت value
        current_str = self.adults_value_element.get_attribute("value")
        current = int(current_str)
        
        while current < target_count:
            self.adults_increment_btn.click(force=True)
            self.page.wait_for_timeout(300)  # مکث طبیعی بین کلیک‌ها
            
            # آپدیت کردن مقدار متغیر در هر بار چرخش حلقه
            current_str = self.adults_value_element.get_attribute("value")
            current = int(current_str)

    def enable_travelling_with_pets(self) -> None:
        """Turn on the 'Traveling with pets' switch."""
        # چک‌باکس حیوانات با CSS مخفی شده و به جای آن یک سوییچ گرافیکی دیده می‌شود، پس از label استفاده می‌کنیم
        pet_label = self.page.locator("label[for='pets']")
        pet_label.wait_for(state="visible", timeout=5000)
        
        # چک می‌کنیم اگر خود چک‌باکس مخفی تیک نخورده است، روی لیبل کلیک کنیم
        if not self.pets_toggle.is_checked():
            pet_label.click(force=True)

    def click_done(self) -> None:
        self.done_button.wait_for(state="visible")
        self.done_button.click(force=True)

    # --- Search ---
    def click_search(self) -> None:
        self.search_button.wait_for(state="visible")
        self.search_button.click(force=True)