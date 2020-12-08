from __future__ import annotations
from browser.firefox import Firefox
from browser.chrome import Chrome
from browser.IBrowser import IBrowser


class BrowserFactory:

    @classmethod
    def get_browser(cls, browser_name: str, profile_dir: str) -> IBrowser:
        browser = None
        if browser_name == 'firefox':
            browser = Firefox(profile_dir)
        if browser_name == 'chrome':
            browser = Chrome(profile_dir)

        return browser
