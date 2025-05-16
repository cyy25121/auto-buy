import pytest
from datetime import datetime, timedelta
from buyer.base import BaseBuyer
from playwright.sync_api import Page

class MockBuyer(BaseBuyer):
    """用於測試的模擬買家類別"""
    def _load_credentials(self):
        self.username = "test_user"
        self.password = "test_pass"

    def login(self):
        return True

    def check_product(self):
        return {"name": "測試商品", "price": 100}

    def purchase(self):
        return True

@pytest.fixture
def buyer(page: Page, mock_url: str) -> MockBuyer:
    """提供測試用的買家實例"""
    return MockBuyer(mock_url, page)

def test_base_buyer_initialization(buyer: MockBuyer, page: Page, mock_url: str):
    """測試 BaseBuyer 初始化"""
    assert buyer.url == mock_url
    assert buyer.page == page
    assert isinstance(buyer.timing_stats, dict)
    assert buyer.username == "test_user"
    assert buyer.password == "test_pass"

def test_wait_for_scheduled_time(buyer: MockBuyer):
    """測試等待排程時間功能"""
    # 測試無排程時間
    buyer.wait_for_scheduled_time(None)
    
    # 測試過去時間
    past_time = (datetime.now() - timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S")
    buyer.wait_for_scheduled_time(past_time)
    
    # 測試未來時間（短暫等待）
    future_time = (datetime.now() + timedelta(seconds=2)).strftime("%Y-%m-%d %H:%M:%S")
    buyer.wait_for_scheduled_time(future_time) 