"""
تنظیمات Playwright و pytest

- مسیر Chrome خودکار تشخیص داده می‌شود
- اسکرین‌شات خودکار هنگام شکست تست
- Logging فعال است
"""

import os
import time
import logging
import pytest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)


# تنظیمات Browser
@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    args = {
        **browser_type_launch_args,
        "headless": False,
        "slow_mo": 400,
        "args": [
            "--start-maximized",
            "--disable-blink-features=AutomationControlled",  # کمتر شبیه ربات
        ],
    }

    # Chrome سیستمی را اگر موجود است استفاده کن، وگرنه Chromium داخلی Playwright
    possible_chrome_paths = [
        "/usr/bin/google-chrome-stable",
        "/usr/bin/google-chrome",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    ]
    for path in possible_chrome_paths:
        if os.path.exists(path):
            args["executable_path"] = path
            break

    return args


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "no_viewport": True,
        "locale": "en-US",
        "ignore_https_errors": True,
    }


# اسکرین‌شات خودکار هنگام شکست
@pytest.fixture(autouse=True)
def screenshot_on_failure(page, request):
    """اسکرین‌شات خودکار هنگام شکست تست."""
    yield
    if request.node.rep_call.failed if hasattr(request.node, "rep_call") else False:
        os.makedirs("screenshots", exist_ok=True)
        filename = f"screenshots/FAIL_{request.node.name}_{int(time.time())}.png"
        page.screenshot(path=filename, full_page=True)
        logging.getLogger(__name__).error(f"[Test Failed] Screenshot: {filename}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """برای دسترسی به نتیجه تست داخل fixture."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
