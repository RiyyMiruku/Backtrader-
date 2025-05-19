import yfinance as yf
import backtrader as bt
import pandas as pd
from datetime import datetime as dt
import numpy as np
import backtrader.feeds as btfeeds
import csv
import subprocess
import stock_data
import backtrader as bt

# import matplotlib.pyplot as plt

# import sys
# print(sys.executable)

tickers    = product_codes = [
    # "AAPL",    # Apple (美股)
    # "TSLA",    # Tesla (美股)
    # "MSFT",    # Microsoft (美股)
    # "SPY",     # S&P 500 ETF (美股指數ETF)
    # "QQQ",     # Nasdaq 100 ETF (美股指數ETF)
    # "GLD",     # SPDR Gold Trust (黃金ETF)
    # "USO",     # United States Oil Fund (石油ETF)
    # "BTC-USD", # Bitcoin (加密貨幣)
    "ETH-USD", # Ethereum (加密貨幣)
    # "EURUSD=X",  # 歐元/美元 (外匯)
    # "JPYUSD=X",  # 美元/日圓 (外匯)
    # "GC=F",    # Gold Futures (黃金期貨)
    # "CL=F",    # Crude Oil Futures (原油期貨)
    # "NDAQ",    # Nasdaq Inc. (交易所相關股票)
    # "NVDA",     # Nvidia (半導體行業)
    "^GSPC"]
data_start   = '2024-01-01'
data_end     = '2025-01-01'
trade_risk = 0.5

class PlotConfig:
    def __init__(self):
        # self.plot_scheme = bt.PlotScheme()

        # 設置繪圖的全域選項
        self.plot_scheme.ytight = False
        self.plot_scheme.yadjust = 0.0
        self.plot_scheme.zdown = True
        self.plot_scheme.tickrotation = 15
        self.plot_scheme.rowsmajor = 5
        self.plot_scheme.rowsminor = 1
        self.plot_scheme.plotdist = 0.0
        self.plot_scheme.grid = True
        self.plot_scheme.style = 'candle'
        self.plot_scheme.volume = True
        self.plot_scheme.voloverlay = True
        self.plot_scheme.volscaling = 0.33
        self.plot_scheme.volpushup = 0.00
        self.plot_scheme.lcolors = bt.plot.tableau10
        self.plot_self.plot_scheme.fmt_x_ticks = '%Y-%m-%d'

    def update(self, **kwargs):
        """允許動態更新設置"""
        for key, value in kwargs.items():
            if hasattr(self.plot_scheme, key):
                setattr(self.plot_scheme, key, value)
            else:
                print(f'Warning: {key} not found in PlotScheme.')

    def get_scheme(self):
        return self.plot_scheme
    

class EMAVegasTunnelStrategy(bt.Strategy):
    params = (
        ('ema_period', 20),       # 計算 EMA 的週期
        ('atr_period', 14),       # ATR 計算週期，用以衡量波動率
        ('atr_multiplier', 1.5),  # ATR 乘數，決定隧道寬度
        ('risk_fraction', 0.1),  # 每筆交易佔總資金比例 (1%)
        ('printlog', True),       # 是否輸出交易日誌
    )

    def __init__(self):
        # 為每個資料建立對應的 EMA、ATR 與隧道上下軌
        self.ema = {}    # EMA 中軸
        self.atr = {}    # ATR 值
        self.upper = {}  # 隧道上軌 = EMA + (atr_multiplier * ATR)
        self.lower = {}  # 隧道下軌 = EMA - (atr_multiplier * ATR)
        self.order = {}  # 跟蹤各品種的訂單狀態

        for d in self.datas:
            # 使用 data 的 _name 作為識別碼，方便管理多產品
            self.ema[d._name] = bt.indicators.EMA(d.close, period=self.p.ema_period)
            self.atr[d._name] = bt.indicators.ATR(d, period=self.p.atr_period)
            self.upper[d._name] = self.ema[d._name] + self.p.atr_multiplier * self.atr[d._name]
            self.lower[d._name] = self.ema[d._name] - self.p.atr_multiplier * self.atr[d._name]
            self.order[d._name] = None

    def next(self):
        for d in self.datas:
            symbol = d._name
            pos = self.getposition(d)

            # 若尚無持倉，當收盤價突破上軌時進場做多
            if not pos:
                if d.close[0] > self.upper[symbol][0]:
                    size = self._calc_position_size(d)
                    self.order[symbol] = self.buy(data=d, size=size)
            else:
                # 若持倉中，當收盤價跌破下軌則平倉
                if d.close[0] < self.lower[symbol][0]:
                    self.order[symbol] = self.close(data=d)

    def _calc_position_size(self, data):
        """
        根據當前帳戶總資金與設定的風險比例，
        以當前收盤價計算適合下單的數量 (僅作簡單示範)
        """
        cash_for_trade = self.broker.getvalue() * self.p.risk_fraction
        size = int(cash_for_trade / data.close[0])
        return size

    def log(self, txt, dt=None):
        if self.p.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()}, {txt}')

    def notify_order(self, order):
        # 忽略尚未完成的訂單
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.data._name}，Price: {order.executed.price:.2f}, Size: {order.executed.size}')
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.data._name}，Price: {order.executed.price:.2f}, Size: {order.executed.size}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'Order Canceled/Margin/Rejected: {order.data._name}')

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'Trade closed for {trade.data._name}, Gross PnL: {trade.pnl:.2f}, Net PnL: {trade.pnlcomm:.2f}')




if __name__ == '__main__':

#BT設置
    cerebro = bt.Cerebro()
    cerebro.addstrategy(EMAVegasTunnelStrategy, risk_fraction = trade_risk)
#數據導入BT
    stock_data.check_and_download_stock_data(tickers)
    for ticker in tickers:
        df = pd.read_csv(f"stock_data/{ticker}.csv", index_col="Date", parse_dates=["Date"])

        # # 確保索引是 datetime
        # if not isinstance(df.index, pd.DatetimeIndex):
        #     df.index = pd.to_datetime(df.index)

        data = bt.feeds.PandasData(dataname =df ,
                                 fromdate = pd.to_datetime(data_start),
                                 todate   = pd.to_datetime(data_end))
        cerebro.adddata(data, name = ticker )
        data.plotinfo.subplot = False 
        data.plotinfo.plotname = f'{ticker}'

#分析數據
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DrawDown')

#初始化 
    cerebro.broker.setcash(100000)
    cerebro.broker.setcommission(commission=0.0002)

#設置交易量
    # cerebro.addsizer(bt.sizers.PercentSizer, percents=90)
    results = cerebro.run()

#輸出數據
    print('夏普比率:', results[0].analyzers.SharpeRatio.get_analysis()['sharperatio'])
    max_drawdown = results[0].analyzers.DrawDown.get_analysis()['max']['drawdown']
    print(f'最大回撤: {max_drawdown:.2f}%')
    print('起始資金:', cerebro.broker.startingcash)  
    print(f'結束資金: {cerebro.broker.get_value():.2f}') 
    print(f'獲利倍率: {((cerebro.broker.get_value() - cerebro.broker.startingcash)/cerebro.broker.startingcash)*100:.4f}%')


    #年化報酬率
    start_date = dt.strptime(data_start, "%Y-%m-%d")
    end_date = dt.strptime(data_end, "%Y-%m-%d")  
    years = (end_date - start_date).days / 365
    annual_return = ((cerebro.broker.get_value() / cerebro.broker.startingcash) ** (1 / years)) - 1
    print(f'年化報酬: {annual_return*100:.2f}%')

#繪圖調整
    # plot_config = PlotConfig()
    # cerebro.plot(plotter= plot_config.get_scheme(), style='candlestick', iplot=True,numfigs=2)
    cerebro.plot(style='candlestick', iplot=True,numfigs=2)