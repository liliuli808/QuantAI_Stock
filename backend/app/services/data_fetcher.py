from abc import ABC, abstractmethod
import akshare as ak
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

class AkShareFetcher(StockDataFetcher):
    def __init__(self, max_requests_per_min: int = 60):
        self.max_requests_per_min = max_requests_per_min
        self.request_timestamps = []

    def _rate_limit(self):
        """
        Simple sliding window rate limiter.
        """
        now = time.time()
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
            # AkShare handles A-shares (e.g., 000001) well.
            # Format usually: '000001' -> convert to specific format if needed or try auto.
            # ak.stock_zh_a_hist expects 6 digit code.
            
            # Start/End date calculation
            end_date = datetime.now()
            # 500 trading days is roughly 2.5 years (730 days) to be safe
            start_date = end_date - timedelta(days=500 * 1.5) 
            
            start_str = start_date.strftime("%Y%m%d")
            end_str = end_date.strftime("%Y%m%d")
            
            logger.info(f"Fetching AkShare data for {ticker} from {start_str}")
            
            # This is specific for A-shares. Ideally we'd detect market.
            # For this MVP, we assume A-share codes (6 digits).
            # If ticker is like 'AAPL', this will fail or we need a configured US fetcher.
            # Assuming User inputs 6-digit code for A-shares or we default to A-shares.
            
            if ticker.isdigit() and len(ticker) == 6:
                df = ak.stock_zh_a_hist(symbol=ticker, start_date=start_str, end_date=end_str, adjust="qfq")
                # Columns: 日期, 开盘, 收盘, 最高, 最低, 成交量, ...
                # Rename to English
                df = df.rename(columns={
                    "日期": "Date",
                    "开盘": "Open", 
                    "收盘": "Close", 
                    "最高": "High", 
                    "最低": "Low", 
                    "成交量": "Volume"
                })
                # Ensure float
                cols = ["Open", "Close", "High", "Low", "Volume"]
                df[cols] = df[cols].astype(float)
                
            else:
                # Fallback or different generic function, akshare has US stock too?
                # ak.stock_us_hist(symbol='105.AAPL', ...) - needs adjustment.
                # For simplicity, let's treat non-digits as US stocks if supported, or error.
                # But requirement said "AkShare + TA-Lib".
                logger.warning(f"Ticker {ticker} format not standard A-share. Trying US logic or returning empty.")
                return pd.DataFrame()

            if df.empty:
                logger.error(f"No data found for {ticker}")
                return pd.DataFrame()

            if len(df) > 500:
                df = df.iloc[-500:]
            
            return df
        except Exception as e:
            logger.error(f"Error fetching history for {ticker}: {str(e)}")
            raise

    def get_current_price(self, ticker: str) -> float:
        self._rate_limit()
        try:
            # ak.stock_zh_a_spot_em() retrieves all spot data (heavy).
            # Better to use history last close or specific single stock spot if available.
            # fast way: fetch 1 day history?
            # Or use ak.stock_zh_a_spot_em() filtered (returns big DF though).
            
            # Let's try getting valid realtime data if possible. 
            # ak.stock_zh_a_spot_em() is real-time but returns ALL stocks.
            # Actually, `stock_zh_a_hist` with today's date might work if market closed or during trading?
            # For efficiency in this specific tool, fetching history (last row) is safest/fastest individual query given constraints.
            
            df = self.fetch_history(ticker, period="5d") # Fetch small history
            if not df.empty:
                return df["Close"].iloc[-1]
            return 0.0
        except Exception as e:
            logger.error(f"Error fetching current price for {ticker}: {str(e)}")
            raise
