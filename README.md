# AUTO BUY

這是一個使用 Python + Playwright 開發的自動購物命令列工具，支援多個電商平台的自動購買功能。

## 支援的平台

- MOMO購物
- PC Home

## 安裝步驟

1. 安裝 Python 3.12 或更新版本
2. 安裝相依套件：
```bash
pip install -r requirements.txt
```
3. 安裝 Playwright：
```bash
playwright install
```

## 環境設定

1. 複製 `.env.example` 為 `.env`
2. 在 `.env` 檔案中填入您的帳號資訊

## 使用方法

基本用法：
```bash
python main.py "商品連結"
```

指定購買時間：
```bash
python main.py "商品連結" --time "2024-03-20 12:00:00"
```

使用 headless 瀏覽器
```bash
python main.py "商品連結" --headless
```

## 注意事項

1. 請確保您的網路連線穩定
2. 建議先使用小額商品測試
3. 某些平台可能有反爬蟲機制，使用時請注意
4. 請遵守各平台的使用規範

## 免責聲明

本工具僅供學習和研究使用，請勿用於商業用途。使用本工具造成的任何損失，開發者概不負責。 