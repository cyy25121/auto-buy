from playwright.sync_api import Page
import logging
import os
from pathlib import Path
from typing import Dict
from buyer.base import BaseBuyer
from dotenv import load_dotenv
import time

logger = logging.getLogger(__name__)

class PChomeBuyer(BaseBuyer):
    def _load_credentials(self):
        """載入登入憑證"""
        env_path = Path('.env')
        if not env_path.exists():
            logger.warning("找不到 .env 檔案，請確保已設定登入資訊")
            return
        
        # 載入 .env 檔案
        load_dotenv(env_path)
        
        # 讀取環境變數
        self.username = os.getenv('PCHOME_USERNAME')
        self.password = os.getenv('PCHOME_PASSWORD')

        if not self.username or not self.password:
            raise ValueError("請在 .env 檔案中設定 PCHOME_USERNAME 和 PCHOME_PASSWORD")

        logger.info(f"已載入 PChome 帳號資訊")

    def login(self):
        """處理 PChome 登入流程"""
        logger.info("開始 PChome 登入流程")
        
        try:
            # 等待登入按鈕出現
            login_button = self.page.get_by_role("button", name="登入")
            login_button.wait_for(state="visible")
            login_button.click()
            
            # 輸入帳號密碼
            account_input = self.page.get_by_placeholder("請輸入手機號碼 或 Email")
            account_input.wait_for(state="visible")
            account_input.fill(self.username)
            
            continue_button = self.page.get_by_role("button", name="繼續")
            continue_button.wait_for(state="visible")
            continue_button.click()
            
            password_input = self.page.get_by_placeholder("請輸入密碼（英文大小寫有差別）")
            password_input.wait_for(state="visible")
            password_input.fill(self.password)
            
            # 點擊登入按鈕
            login_button = self.page.get_by_role("button", name="登入")
            login_button.wait_for(state="visible")
            login_button.click()

            # 這邊可能要做認證，點擊送出進行 Email 認證
            submit_button = self.page.get_by_role("button", name="送出")
            submit_button.wait_for(state="visible")
            submit_button.click()

            # 等待使用者輸入驗證碼
            logger.info("請檢查您的 Email 並輸入驗證碼:")
            verification_code = input("請輸入驗證碼: ")
            
            # 輸入驗證碼
            self.page.locator(".c-input__captcha > input").first.fill(verification_code[0])
            self.page.locator("div:nth-child(2) > .c-input__captcha > input").fill(verification_code[1])
            self.page.locator("div:nth-child(3) > .c-input__captcha > input").fill(verification_code[2])
            self.page.locator("div:nth-child(4) > .c-input__captcha > input").fill(verification_code[3])
            self.page.locator("div:nth-child(5) > .c-input__captcha > input").fill(verification_code[4])
            self.page.locator("div:nth-child(6) > .c-input__captcha > input").fill(verification_code[5])
            
            # 點擊確認按鈕
            self.page.get_by_role("button", name="確認").click()
            self.page.get_by_role("button", name="取消").click()

            logger.info("PChome 登入成功")
            
        except Exception as e:
            logger.error(f"PChome 登入失敗: {str(e)}")
            # 保存錯誤截圖
            self.page.screenshot(path=f"login_error_{int(time.time())}.png")
            raise

    def check_product(self) -> Dict:
        """檢查商品資訊"""
        logger.info("檢查商品資訊")
        
        try:
            # 等待主要內容載入
            self.page.wait_for_selector("div.o-prodMainName", timeout=5000)
            
            # 使用單一 evaluate 呼叫取得所有商品資訊
            product_info = self.page.evaluate('''() => {
                const result = {
                    name: null,
                    price: null,
                    original_price: null,
                    has_stock: false
                };
                
                // 取得商品名稱
                const nameElement = document.querySelector('h1.o-prodMainName__grayDarkest') || 
                                  document.querySelector('h1[data-regression="prod_info_name"]') ||
                                  document.querySelector('div.o-prodMainName h1');
                if (nameElement) {
                    result.name = nameElement.textContent.trim();
                }
                
                // 取得價格資訊
                const priceBox = document.querySelector('div.o-prodPrice__priceBox');
                if (priceBox) {
                    // 折扣價
                    const discountElement = priceBox.querySelector('div.o-prodPrice__price--xxxl700Primary');
                    if (discountElement) {
                        result.price = parseInt(discountElement.textContent.replace(/[^0-9]/g, ''));
                    }
                    
                    // 原價
                    const originalElement = priceBox.querySelector('div.o-prodPrice__originalPrice--m500Gray');
                    if (originalElement) {
                        result.original_price = parseInt(originalElement.textContent.replace(/[^0-9]/g, ''));
                    }
                }
                
                // 檢查庫存狀態
                const buyButton = document.querySelector('button[data-regression="product_button_buyNow"]');
                const notifyButtons = Array.from(document.querySelectorAll('button span.btn__text')).filter(el => el.textContent.includes('有貨通知我'));
                result.has_stock = buyButton && notifyButtons.length === 0;
                
                return result;
            }''')
            
            # 驗證結果
            if not product_info['name']:
                raise ValueError("無法取得商品名稱")
            
            if not product_info['price'] and not product_info['original_price']:
                raise ValueError("無法取得商品價格")
            
            # 如果沒有折扣價，使用原價
            if not product_info['price']:
                product_info['price'] = product_info['original_price']
            
            logger.info(f"商品名稱: {product_info['name']}")
            logger.info(f"商品價格: {product_info['price']}")
            logger.info(f"商品原價: {product_info['original_price']}")
            logger.info(f"是否有庫存: {product_info['has_stock']}")
            
            return product_info
            
        except Exception as e:
            logger.error(f"檢查商品資訊時發生錯誤: {str(e)}")
            self.page.screenshot(path=f"product_check_error_{int(time.time())}.png")
            raise

    def purchase(self):
        """執行購買流程"""
        logger.info("開始購買流程")
        
        try:
            # 檢查是否有庫存
            product_info = self.check_product()
            if not product_info["has_stock"]:
                raise Exception("商品目前無庫存")
            
            # 點擊立即購買按鈕
            buy_button = self.page.wait_for_selector("button[data-regression='product_button_buyNow']", timeout=5000)
            if not buy_button:
                raise Exception("找不到立即購買按鈕")
            
            buy_button.click()
            logger.info("已點擊立即購買按鈕")
            
            # 等待購物車頁面載入
            self.page.wait_for_selector('.cart-page', timeout=10000)
            logger.info("購物車頁面已載入")
            
            # 選擇付款方式（預設選擇信用卡付款）
            self.page.click('label:has-text("信用卡")')
            logger.info("已選擇信用卡付款")
            
            # 選擇配送方式（預設選擇宅配）
            self.page.click('label:has-text("宅配")')
            logger.info("已選擇宅配")
            
            # 確認訂單
            self.page.click('button:has-text("確認結帳")')
            logger.info("已點擊確認結帳")
            
            # 等待訂單確認
            self.page.wait_for_selector('.order-success', timeout=30000)
            logger.info("PChome 購買完成")
            
        except Exception as e:
            logger.error(f"PChome 購買過程發生錯誤: {str(e)}")
            self.page.screenshot(path=f"purchase_error_{int(time.time())}.png")
            raise 