import random
import time
import logging

logger = logging.getLogger(__name__)

class UserAgentManager:
    """User-Agent 管理工具"""
    
    # 常見的作業系統
    _OS_LIST = [
        'Macintosh; Intel Mac OS X 10_15_7',
        'Windows NT 10.0; Win64; x64',
        'Windows NT 10.0; WOW64',
        'Windows NT 6.1; Win64; x64',
        'X11; Linux x86_64',
        'X11; Ubuntu; Linux x86_64'
    ]
    
    # Chrome 版本範圍
    _CHROME_VERSIONS = [
        '120.0.0.0',
        '121.0.0.0',
        '122.0.0.0',
        '123.0.0.0'
    ]
    
    @classmethod
    def get_random_user_agent(cls) -> str:
        """取得隨機的 User-Agent"""
        os_info = random.choice(cls._OS_LIST)
        chrome_version = random.choice(cls._CHROME_VERSIONS)
        
        user_agent = f'Mozilla/5.0 ({os_info}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36'
        return user_agent
    
    @classmethod
    def get_mobile_user_agent(cls) -> str:
        """取得隨機的手機版 User-Agent"""
        mobile_devices = [
            'iPhone; CPU iPhone OS 16_0 like Mac OS X',
            'Linux; Android 13; SM-S908B',
            'Linux; Android 13; Pixel 7',
            'Linux; Android 12; SM-S906N',
            'iPhone; CPU iPhone OS 15_0 like Mac OS X',
            'Linux; Android 12; Pixel 6'
        ]
        
        device = random.choice(mobile_devices)
        chrome_version = random.choice(cls._CHROME_VERSIONS)
        
        if 'iPhone' in device:
            return f'Mozilla/5.0 ({device}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
        else:
            return f'Mozilla/5.0 ({device}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Mobile Safari/537.36' 
        
class TimingContext:
    """計時器上下文管理器"""
    def __init__(self, description: str):
        self.description = description
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.time()
        logger.info(f"開始{self.description}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        logger.info(f"完成{self.description}，耗時: {duration:.2f} 秒") 