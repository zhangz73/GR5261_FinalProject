import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
from yahoo_finance_api2 import share
from datetime import datetime
from tqdm import tqdm

def get_single_stock_scraper(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}/history?period1=1457568000&period2=1615334400&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    ticker_arr, date_arr, open_arr, high_arr, low_arr, close_arr, adj_arr, volume_arr = [], [], [], [], [], [], [], []
    rows = soup.find_all('tbody')[0].find_all('tr')
    for row in rows:
        elements = row.find_all('td')
        if len(elements) >= 7:
            date_arr.append(elements[0].getText())
            open_arr.append(elements[1].getText())
            high_arr.append(elements[2].getText())
            low_arr.append(elements[3].getText())
            close_arr.append(elements[4].getText())
            adj_arr.append(elements[5].getText())
            volume_arr.append(elements[6].getText())
            ticker_arr.append(ticker)
    return pd.DataFrame.from_dict({"Ticker": ticker_arr, "Date": date_arr, "Open": open_arr, "High": high_arr, "Low": low_arr, "Close": close_arr, "Adj.Close": adj_arr, "Volume": volume_arr})

def get_single_stock_yahoo(ticker):
    stock = share.Share(ticker)
#    result_lst = stock.get_historical('2016-01-01', '2021-03-10')
#    ticker_arr, date_arr, open_arr, high_arr, low_arr, close_arr, adj_arr, volume_arr = [], [], [], [], [], [], [], []
#    for result in result_lst:
#        date_arr.append(result['Date'])
#        open_arr.append(result['Open'])
#        high_arr.append(result['High'])
#        low_arr.append(result['Low'])
#        close_arr.append(result['Close'])
#        adj_arr.append(result['Adj_Close'])
#        volume_arr.append(result['Volume'])
#        ticker_arr.append(ticker)
#    return pd.DataFrame.from_dict({"Ticker": ticker_arr, "Date": date_arr, "Open": open_arr, "High": high_arr, "Low": low_arr, "Close": close_arr, "Adj.Close": adj_arr, "Volume": volume_arr})
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?symbol={ticker}&period1=1457568000&period2=1615334400&interval=1d&includePrePost=true&events=div%7Csplit%7Cearn&lang=en-US&region=US&crumb=t5QZMhgytYZ&corsDomain=finance.yahoo.com"
#    data = stock.get_historical(share.PERIOD_TYPE_DAY, 1250, share.FREQUENCY_TYPE_DAY, 1)
    data = requests.get(url).json()
    data = data["chart"]["result"][0]
    date_arr = [datetime.fromtimestamp(x).strftime("%Y-%m-%d") for x in data["timestamp"]]
    data = data["indicators"]["quote"][0]
    data["date"] = date_arr
    data["ticker"] = [ticker] * len(date_arr)
    data.pop("timestamp", None)
    return pd.DataFrame.from_dict(data)

def get_sp500_yahoo():
    scope = list(pd.read_csv("SP500table.csv")["Ticker"])
    df_ret = None
    err_lst = []
    for ticker in tqdm(scope):
        try:
            df = get_single_stock_yahoo(ticker.replace(".", "-"))
            if df_ret is None:
                df_ret = df
            else:
                df_ret = df_ret.append(df, ignore_index=True)
        except:
            err_lst.append(ticker)
    print("These stocks are not collected: " + str(err_lst))
    return df_ret

df = get_sp500_yahoo()
df = df.sort_values(["ticker", "date"])
df = df[["ticker", "date", "open", "high", "low", "close", "volume"]]
print(df.shape)
df.to_csv("SP500_Historical_Prices.csv", index=False)
