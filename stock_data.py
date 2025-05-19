import os
import datetime
import yfinance as yf
import pandas as pd
import sys
import requests

# 需要檢查的股票列表
stocks = ["TSLA"]


# 檢查資料夾中是否有該股票的近十年資料
def check_and_download_stock_data(stocks):

    backtest_years = 5
    # SOCKS5 代理
    proxy = "http://67.43.228.250:28037"

    # session = requests.Session()
    # session.proxies = {"https": proxy, "http": proxy}

    # 設定資料夾路徑
    data_folder = './stock_data/'

    # 確保資料夾存在
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    for stock in stocks:

        # 設定檔案路徑（以股票代碼命名的CSV檔案）
        file_path = os.path.join(data_folder, f'{stock}.csv')

        # 檢查檔案是否已存在
        if os.path.exists(file_path):
            print(f'{stock}資料已存在，跳過下載.')

        else:
            
            print(f'{stock}資料不存在，開始下載...')
            
            # 使用yfinance下載資料
            download_via_yfinance(stock, file_path, backtest_years, proxy)

            # # 使用Rapid API下載資料
            # download_via_RapidAPI(stock, file_path, backtest_years, session)



def download_via_RapidAPI(ticker, file_path, backtest_years):

    # API 參數
    headers = {
        "X-RapidAPI-Key": "aea7832162msha3884e3f464917bp102d2ajsn104282050d44",
        "X-RapidAPI-Host": "yahoo-finance15.p.rapidapi.com"
    }

    url = f"https://yahoo-finance15.p.rapidapi.com/api/v1/markets/stock/quotes?ticker={ticker}"
        
    response = requests.get(url, headers=headers)
        
    if response.status_code == 200:
        data = response.json()
        history = data.get("history", [])
            
        if history:
            df = pd.DataFrame(history)
            df.to_csv(file_path, index=False)
            print(f"✅ {ticker} 數據已儲存為 {ticker}.csv")
        else:
            print(f"⚠️ {ticker} 沒有數據")
    else:
        print(f"❌ 無法獲取 {ticker}，錯誤碼: {response.status_code}")


def download_via_yfinance(stock, file_path, backtest_years,proxy):
    # 下載最近年的資料
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=365*backtest_years)).strftime('%Y-%m-%d')
    df = pd.DataFrame(yf.download(stock, start=start_date, end=end_date,auto_adjust=True,threads=False))
    if not df.empty:    
        print(df.columns)  
        df.columns = ["close", "high", "low", "open", "volume"]
        df.to_csv(file_path, header=True)
    


if __name__ == "__main__":  
    check_and_download_stock_data(stocks)

