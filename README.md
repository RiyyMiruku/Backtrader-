# Backtrader 策略回測專案

本專案使用 [Backtrader](https://www.backtrader.com/) 進行多品種金融商品的量化策略回測，並結合 [yfinance](https://github.com/ranaroussi/yfinance) 自動下載歷史資料。策略以 EMA + ATR 隧道為主，支援多商品同時回測。

## 專案結構

```
2mode.py                # 主程式，策略定義與回測流程
stock_data.py           # 股票/商品歷史資料自動下載
get_ips.py              # 取得代理伺服器IP（如需）
test_ip.py              # 測試代理IP可用性
stock_data/             # 儲存各商品歷史資料的資料夾（CSV檔）
    ^GSPC.csv
    0050.TW.csv
    ...
```

## 主要檔案說明

- [`2mode.py`](2mode.py)：  
  - 定義 `EMAVegasTunnelStrategy` 策略（EMA+ATR 隧道突破進出場）。
  - 自動載入 `stock_data/` 內的資料，或呼叫 [`stock_data.check_and_download_stock_data`](stock_data.py) 下載。
  - 執行回測、計算夏普比率、最大回撤、年化報酬等指標，並繪製圖表。

- [`stock_data.py`](stock_data.py)：  
  - 檢查指定商品的歷史資料是否存在，若無則自動下載（預設用 yfinance）。
  - 支援自訂代理伺服器。

- [`get_ips.py`](get_ips.py)、[`test_ip.py`](test_ip.py)：  
  - 用於獲取與測試代理伺服器 IP（如需突破網路限制時使用）。

## 如何使用

1. 安裝必要套件：
    ```sh
    pip install backtrader yfinance pandas numpy
    ```

2. 將欲回測的商品代碼填入 [`2mode.py`](2mode.py) 的 `tickers` 清單。

3. 執行主程式：
    ```sh
    python 2mode.py
    ```

4. 回測結果將顯示夏普比率、最大回撤、年化報酬等，並自動繪圖。

## 策略邏輯簡述

- **進場**：收盤價突破 EMA+ATR 隧道上軌時做多。
- **出場**：收盤價跌破 EMA-ATR 隧道下軌時平倉。
- **部位管理**：每筆交易風險可自訂（預設 10%）。

## 注意事項

- 請確保 `stock_data/` 資料夾有寫入權限。
- 若遇到資料下載失敗，可檢查網路或代理設定。
- 若需回測台股、期貨、加密貨幣等，請確認 yfinance 是否支援該商品。

---

如需擴充策略或資料來源，請參考原始碼註解。
