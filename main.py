#!/usr/bin/env python3
import click
from playwright.sync_api import sync_playwright, Page
from urllib.parse import urlparse
import time
import logging
from typing import Optional
from utils import UserAgentManager, TimingContext
from buyer.base import BaseBuyer

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PlatformFactory:
    """平台工廠類別"""
    @staticmethod
    def create_buyer(url: str, page: Page) -> BaseBuyer:
        domain = urlparse(url).netloc
        
        if "24h.pchome.com.tw" in domain:
            from buyer.pchome import PChomeBuyer
            return PChomeBuyer(url, page)
        elif "momoshop" in domain:
            from buyer.momo import MomoBuyer
            return MomoBuyer(url, page)
        else:
            raise ValueError(f"不支援的平台: {domain}")

def run_buyer(url: str, scheduled_time: Optional[str] = None, headless: bool = False):
    """執行自動購買流程"""
    total_start_time = time.time()
    
    with sync_playwright() as p:
        with TimingContext("啟動瀏覽器"):
            browser = p.chromium.launch(headless=headless)
            
            # 建立瀏覽器上下文，設定隨機 User-Agent
            user_agent = UserAgentManager.get_random_user_agent()
            logger.info(f"使用 User-Agent: {user_agent}")
            
            context = browser.new_context(
                user_agent=user_agent,
                viewport={'width': 1280, 'height': 800}
            )
            page = context.new_page()
        
        try:
            # 建立對應平台的購買器
            with TimingContext("初始化購買器"):
                buyer = PlatformFactory.create_buyer(url, page)
            
            # 等待預定時間
            if scheduled_time:
                with TimingContext(f"等待預定時間 {scheduled_time}"):
                    buyer.wait_for_scheduled_time(scheduled_time)
            
            # 訪問商品頁面
            with TimingContext("載入商品頁面"):
                page.goto(url)
            
            # 檢查商品
            with TimingContext("檢查商品資訊"):
                product_info = buyer.check_product()
                logger.info(f"商品資訊: {product_info}")
            
            total_time = time.time() - total_start_time
            logger.info(f"購買流程完成，總耗時: {total_time:.2f} 秒")
            
        except Exception as e:
            total_time = time.time() - total_start_time
            logger.error(f"發生錯誤: {str(e)}")
            logger.error(f"執行失敗，總耗時: {total_time:.2f} 秒")
            
            if not headless:
                timestamp = int(time.time())
                page.screenshot(path=f"error_{timestamp}.png")
        finally:
            with TimingContext("關閉瀏覽器"):
                context.close()
                browser.close()

@click.command()
@click.argument('url')
@click.option('--time', '-t', help='預定購買時間 (格式: YYYY-MM-DD HH:MM:SS)')
@click.option('--headless', '-h', is_flag=True, help='使用無頭模式（不顯示瀏覽器視窗）')
def main(url: str, time: Optional[str] = None, headless: bool = False):
    """
    自動購買程式
    
    URL: 商品連結
    
    範例:
    \b
    # 一般模式（顯示瀏覽器）
    python auto_buy.py "商品連結"
    
    # 無頭模式（背景執行）
    python auto_buy.py -h "商品連結"
    
    # 指定時間購買
    python auto_buy.py -t "2024-03-20 12:00:00" "商品連結"
    """
    try:
        if headless:
            logger.info("使用無頭模式執行")
        run_buyer(url, time, headless)
    except Exception as e:
        logger.error(f"程式執行錯誤: {str(e)}")

if __name__ == '__main__':
    main() 