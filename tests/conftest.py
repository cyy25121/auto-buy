import pytest
from playwright.sync_api import sync_playwright, Page
from typing import Generator

@pytest.fixture
def page() -> Generator[Page, None, None]:
    """提供 Playwright Page 物件的 fixture"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        yield page
        context.close()
        browser.close()

@pytest.fixture
def mock_url() -> str:
    """測試用的模擬 URL"""
    return "https://example.com/product" 