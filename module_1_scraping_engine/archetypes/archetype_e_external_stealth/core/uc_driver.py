"""
Archetype E Stealth Toolkit: Undetected ChromeDriver (UC Mode) Wrapper
Handles heavy JS-rendered pages and Cloudflare Turnstile challenges.
"""
from typing import Optional
import logging

logger = logging.getLogger("UCDriverWrapper")


class UCDriverWrapper:
    def __init__(self, headless: bool = True, proxy: Optional[str] = None):
        self.headless = headless
        self.proxy = proxy
        self.driver = None

    def get_driver(self):
        """Initializes SeleniumBase Driver in undetected UC mode."""
        try:
            from seleniumbase import Driver
            self.driver = Driver(
                uc=True,
                headless=self.headless,
                proxy=self.proxy,
                incognito=True,
                agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            return self.driver
        except ImportError:
            logger.warning("[UCDriverWrapper] seleniumbase not installed. UC mode browser unavailable.")
            return None

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
