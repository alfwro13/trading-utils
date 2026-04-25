import logging
import os
import pandas as pd
import yfinance as yf
from tqdm import tqdm
from yahoo_earnings_calendar import YahooEarningsCalendar

from common import ALL_LISTED_TICKERS_FILE, LARGE_CAP_TICKERS_FILE
from common.filesystem import file_exists, output_dir
# Added the missing import below
from common.market_data import download_ticker_data

yec = YahooEarningsCalendar()

def download_earnings_between(date_from, date_to):
    try:
        return yec.earnings_between(date_from, date_to)
    except:
        return {}

def download_ticker_with_interval(ticker, period, interval):
    try:
        opts = dict(
            tickers=ticker,
            period=period,
            interval=interval,
            auto_adjust=True,
            progress=False,
        )
        df = yf.download(**opts)
        df.to_csv(f"{output_dir()}/{ticker}-{interval}.csv")
        return df
    except Exception as e:
        print("ERROR: Unable to download {}".format(ticker), e)

def load_all_tickers(market_type="all"):
    file_to_load = ALL_LISTED_TICKERS_FILE
    if market_type == "large-cap":
        if file_exists(LARGE_CAP_TICKERS_FILE):
            file_to_load = LARGE_CAP_TICKERS_FILE
        else:
            logging.warning(
                f"Unable to find {LARGE_CAP_TICKERS_FILE} please see README or download it from BarChart"
            )
            return []
    return pd.read_csv(file_to_load).Symbol.tolist()

def get_cached_data(symbol, start, end, force_download=False):
    out_dir = "output"
    os.makedirs(out_dir, exist_ok=True)
    cache_file = os.path.join(out_dir, f"{symbol}_{start}_{end}.csv")

    if os.path.exists(cache_file) and not force_download:
        logging.info(f"Loading cached data for {symbol} from {cache_file}")
        return pd.read_csv(cache_file, index_col=0, parse_dates=True)
    else:
        logging.info(f"Downloading fresh data for {symbol}")
        df = download_ticker_data(symbol, start=start, end=end)
        df.to_csv(cache_file)
        return df

def download_tickers_data(tickers, start, end):
    print(f"Downloading data for {len(tickers)} tickers")
    bad_tickers = []
    
    # We need the output directory path
    out_dir = output_dir()

    for t in tqdm(tickers):
        try:
            # Download the data
            df = download_ticker_data(t, start, end)
            
            # THE FIX: Save the data to a CSV file so the enricher can find it
            if not df.empty:
                df.to_csv(f"{out_dir}/{t}.csv")
            else:
                bad_tickers.append(dict(symbol=t, reason="No data returned from Yahoo Finance"))
                
        except Exception as e:
            bad_tickers.append(dict(symbol=t, reason=str(e)))

    if bad_tickers:
        print(f"Unable to download {len(bad_tickers)} tickers. Check the logs for details.")


large_cap_companies = load_all_tickers(market_type="large-cap")
