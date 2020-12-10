from __future__ import annotations
from browser.firefox import Firefox
from browser.chrome import Chrome
from browser.IBrowser import IBrowser


class BrowserFactory:

    @classmethod
    def get_browser(cls, browser_name: str) -> IBrowser:
        """
        return a browser object
        """
        browser = None
        if browser_name == 'firefox':
            browser = Firefox()
        if browser_name == 'chrome':
            browser = Chrome()

        return browser
