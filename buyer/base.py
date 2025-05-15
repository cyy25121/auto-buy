from abc import ABC, abstractmethod
from typing import Dict, Optional
from playwright.sync_api import Page
import datetime
import time
import logging

logger = logging.getLogger(__name__)

class BaseBuyer(ABC):
    """自動購買基礎類別"""
    def __init__(self, url: str, page: Page):
        self.url = url
        self.page = page
        self.timing_stats = {}  
        self._load_credentials()

    @abstractmethod
    def _load_credentials(self):
        """載入平台帳號密碼"""
        pass

    @abstractmethod
    def login(self):
        """執行登入流程"""
        pass

    @abstractmethod
    def check_product(self) -> Dict:
        """檢查商品資訊"""
        pass

    @abstractmethod
    def purchase(self):
        """執行購買流程"""
        pass

    def wait_for_scheduled_time(self, scheduled_time: Optional[str]):
        """等待直到指定時間"""
        if not scheduled_time:
            return
        
        target_time = datetime.datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M:%S")
        while datetime.datetime.now() < target_time:
            time.sleep(1)
            logger.info(f"等待中... 目標時間: {scheduled_time}")