import os
from typing import Dict
from playwright.sync_api import Page
import logging
from dotenv import load_dotenv
import time
from buyer.base import BaseBuyer

logger = logging.getLogger(__name__)

class MomoBuyer(BaseBuyer):
    """MOMO購物平台實作"""
    
    def __init__(self, url: str, page: Page):
        super().__init__(url, page)
        self.i_code = self._extract_i_code(url)
        
    def _extract_i_code(self, url: str) -> str:
        """從URL中提取商品代碼"""
        try:
            i_code = url.split('i_code=')[1].split('&')[0]
            return i_code
        except:
            raise ValueError("無法從URL中提取商品代碼，請確認連結格式是否正確")
    
    def _load_credentials(self):
        """載入MOMO帳號密碼"""
        load_dotenv()
        self.username = os.getenv('MOMO_USERNAME')
        self.password = os.getenv('MOMO_PASSWORD')
        
        if not self.username or not self.password:
            raise ValueError("請在.env檔案中設定MOMO_USERNAME和MOMO_PASSWORD")
    
    def login(self):
        """執行MOMO登入流程"""
        try:
            # 點擊登入按鈕
            self.page.click('a.loginBtn')
            
            # 填寫帳號密碼
            self.page.fill('#memId', self.username)
            self.page.fill('#passwd', self.password)
            
            # 點擊登入
            self.page.click('button.login')
            
            # 等待登入完成
            self.page.wait_for_selector('a.userName', timeout=10000)
            logger.info("MOMO登入成功")
            
        except Exception as e:
            logger.error(f"MOMO登入失敗: {str(e)}")
            self.page.screenshot(path=f"login_error_{int(time.time())}.png")
            raise
    
    def check_product(self) -> Dict:
        """檢查商品資訊"""
        try:
            # 等待商品資訊載入
            self.page.wait_for_selector('#osmGoodsName', timeout=10000)
            
            # 使用單一 evaluate 呼叫取得所有商品資訊
            product_info = self.page.evaluate('''() => {
                const result = {
                    name: null,
                    price: {
                        original: null,
                        sale: null,
                        final: null
                    },
                    can_buy: false,
                    i_code: null
                };
                
                // 取得商品名稱
                const nameElement = document.querySelector('#osmGoodsName');
                if (nameElement) {
                    result.name = nameElement.textContent.trim();
                }
                
                // 取得價格資訊
                const priceElements = document.querySelectorAll('.prdPrice li');
                priceElements.forEach(element => {
                    const text = element.textContent;
                    const priceElement = element.querySelector('.seoPrice');
                    if (!priceElement) return;
                    
                    const price = parseInt(priceElement.textContent.replace(/[^0-9]/g, ''));
                    
                    if (text.includes('市售價')) {
                        result.price.original = price;
                    } else if (text.includes('促銷價')) {
                        result.price.sale = price;
                    } else if (text.includes('折扣後價格')) {
                        result.price.final = price;
                    }
                });
                
                // 檢查購買按鈕狀態
                const buyYes = document.querySelector('#buy_yes');
                const buyNo = document.querySelector('#buy_no');
                
                if (buyYes) {
                    const buyYesStyle = window.getComputedStyle(buyYes);
                    result.can_buy = buyYesStyle.display !== 'none';
                }
                
                if (!result.can_buy && buyNo) {
                    const buyNoStyle = window.getComputedStyle(buyNo);
                    result.can_buy = buyNoStyle.display === 'none';
                }
                
                return result;
            }''')
            
            # 加入商品代碼
            product_info['i_code'] = self.i_code
            
            # 驗證結果
            if not product_info['name']:
                raise ValueError("無法取得商品名稱")
            
            if not any(product_info['price'].values()):
                raise ValueError("無法取得商品價格")
            
            logger.info(f"商品名稱: {product_info['name']}")
            logger.info(f"價格資訊: {product_info['price']}")
            logger.info(f"可購買: {product_info['can_buy']}")
            
            return product_info
            
        except Exception as e:
            logger.error(f"檢查商品資訊失敗: {str(e)}")
            self.page.screenshot(path=f"product_check_error_{int(time.time())}.png")
            raise
    
    def purchase(self):
        """執行購買流程"""
        try:
            # 檢查是否可購買
            buy_button = self.page.query_selector('#buy_yes')
            if not buy_button or buy_button.is_hidden():
                raise ValueError("商品目前無法購買")
            
            # 點擊購買按鈕
            self.page.click('#buy_yes a.buynow')
            
            # 等待購物車頁面載入
            self.page.wait_for_selector('.checkoutBtn', timeout=10000)
            
            # 點擊結帳按鈕
            self.page.click('.checkoutBtn')
            
            # 等待結帳頁面載入
            self.page.wait_for_selector('#orderSendBtn', timeout=10000)
            
            # 送出訂單
            self.page.click('#orderSendBtn')
            
            logger.info("MOMO購買流程完成")
            
        except Exception as e:
            logger.error(f"購買失敗: {str(e)}")
            self.page.screenshot(path=f"purchase_error_{int(time.time())}.png")
            raise 