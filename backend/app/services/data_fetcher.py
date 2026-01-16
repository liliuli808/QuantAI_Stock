from abc import ABC, abstractmethod
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockDataFetcher(ABC):
    @abstractmethod
    def fetch_history(self, ticker: str, period: str = "500d") -> pd.DataFrame:
        """
        Fetch historical stock data.
        Returns a DataFrame with columns: Open, High, Low, Close, Volume.
        """
        pass

    @abstractmethod
    def get_current_price(self, ticker: str) -> float:
        """
        Get the current price of the stock.
        """
        pass

class YFinanceFetcher(StockDataFetcher):
    def __init__(self, max_requests_per_min: int = 60):
        self.max_requests_per_min = max_requests_per_min
        self.request_timestamps = []

    def _rate_limit(self):
        """
        Simple sliding window rate limiter.
        """
        now = time.time()
        # Remove timestamps older than 1 minute
        self.request_timestamps = [t for t in self.request_timestamps if now - t < 60]
        
        if len(self.request_timestamps) >= self.max_requests_per_min:
            sleep_time = 60 - (now - self.request_timestamps[0])
            if sleep_time > 0:
                logger.warning(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds.")
                time.sleep(sleep_time)
        
        self.request_timestamps.append(time.time())

    def fetch_history(self, ticker: str, period: str = "500d") -> pd.DataFrame:
        self._rate_limit()
        try:
            # yfinance allows fetching by period string (e.g., '1mo', '1y', 'max')
            # For 500 days specifically, we can use '2y' and slice, or just '2y' is close enough/safe.
            # yfinance accepts: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            
            # Map '500d' to something yfinance understands or use validation
            yf_period = "2y" 
            
            logger.info(f"Fetching data for {ticker} for period {yf_period}")
            ticker_obj = yf.Ticker(ticker)
            df = ticker_obj.history(period=yf_period)
            
            if df.empty:
                logger.error(f"No data found for {ticker}")
                return pd.DataFrame()

            # Ensure we strictly return the last N rows if needed, typically analysis uses available data.
            # But the requirement says "500天". 
            if len(df) > 500:
                df = df.iloc[-500:]
            
            return df
        except Exception as e:
            logger.error(f"Error fetching history for {ticker}: {str(e)}")
            raise

    def get_current_price(self, ticker: str) -> float:
        self._rate_limit()
        try:
            ticker_obj = yf.Ticker(ticker)
            # fast_info is often faster/reliable for current price
            return ticker_obj.fast_info.last_price
        except Exception as e:
            logger.error(f"Error fetching current price for {ticker}: {str(e)}")
            # Fallback to history
            try:
                df = self.fetch_history(ticker, period="1d")
                if not df.empty:
                    return df["Close"].iloc[-1]
            except:
                pass
            raise
