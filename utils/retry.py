"""
utils/retry.py
--------------
Retry decorator با exponential backoff برای عملیات‌های شبکه‌ای ناپایدار.
"""

import time
import logging
import functools

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError

logger = logging.getLogger(__name__)


def retry(max_attempts: int = 3, delay: float = 2.0):
    """
    هر تابعی که با این decorator مزین شود، در صورت خطای Playwright
    تا max_attempts بار با تاخیر exponential دوباره تلاش می‌کند.

    مثال:
        @retry(max_attempts=3, delay=2.0)
        def click_login(self):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except (PlaywrightTimeoutError, PlaywrightError, Exception) as e:
                    last_error = e
                    wait = delay * (2 ** (attempt - 1))   # 2s → 4s → 8s
                    logger.warning(
                        f"[Retry {attempt}/{max_attempts}] {func.__name__} "
                        f"→ {type(e).__name__}: {e} — retrying in {wait:.1f}s"
                    )
                    time.sleep(wait)
            logger.error(f"[Failed] {func.__name__} after {max_attempts} attempts.")
            raise last_error
        return wrapper
    return decorator
