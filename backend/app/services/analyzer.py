import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, Any

try:
    import talib
except ImportError:
    # Mocking talib for environments where C-lib is missing (local dev without compiled lib)
    class MockTalib:
        def __getattr__(self, name):
            def mock_func(*args, **kwargs):
                # Return dummy values: mostly arrays of same length as input
                if len(args) > 0:
                    arr = args[0]
                    if isinstance(arr, np.ndarray):
                        if name == 'BBANDS':
                            return arr, arr, arr
                        if name == 'MACD':
                            return arr, arr, arr
                        if name == 'STOCH':
                            return arr, arr
                        return arr
                return 0.0
            return mock_func
    talib = MockTalib()
    print("WARNING: TA-Lib not found. Using Mock object for local dev.")

@dataclass
class AnalysisResult:
    score: float
    summary: str
    indicators: Dict[str, Any]
    signal: str 

class TechnicalAnalyzer:
    def analyze(self, df: pd.DataFrame) -> AnalysisResult:
        """
        Perform comprehensive technical analysis on the dataframe using TA-Lib.
        Expects columns: Open, High, Low, Close, Volume
        """
        if df.empty:
            return AnalysisResult(0, "No data", {}, "HOLD")

        # TA-Lib requires numpy arrays of float type
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values

        # 1. Calculate Indicators using TA-Lib
        # MACD (fast=12, slow=26, signal=9)
        macd, macd_signal, macd_hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        
        # RSI (window=14)
        rsi = talib.RSI(close, timeperiod=14)

        # KDJ (Stochastic) - TA-Lib calls it STOCH
        # fastk_period=9, slowk_period=3 (Signal), slowd_period=3 (Window) usually
        # But typical KDJ: fastk=9, K=SMA(fastk, 3), D=SMA(K, 3), J=3K-2D.
        # STOCH gives K and D (slowk, slowd).
        k, d = talib.STOCH(high, low, close, 
                           fastk_period=9, 
                           slowk_period=3, 
                           slowk_matype=0, 
                           slowd_period=3, 
                           slowd_matype=0)
        j = 3 * k - 2 * d

        # Bollinger Bands (timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        upper, middle, lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        
        # MA
        ma5 = talib.SMA(close, timeperiod=5)
        ma20 = talib.SMA(close, timeperiod=20)
        
        # Safely get latest values (handle NaNs at start)
        # We need the last valid value or just the last element
        def safe_get(arr):
            val = arr[-1]
            return float(val) if not np.isnan(val) else 0.0

        latest_rsi = safe_get(rsi)
        latest_macd_diff = safe_get(macd_hist) # TA-Lib MACD Hist IS the "diff" usually (MACD - Signal)
        latest_macd = safe_get(macd)
        latest_macd_signal = safe_get(macd_signal)
        latest_k = safe_get(k)
        latest_d = safe_get(d)
        latest_j = safe_get(j)
        latest_ma5 = safe_get(ma5)
        latest_ma20 = safe_get(ma20)
        latest_bb_low = safe_get(lower)
        latest_bb_high = safe_get(upper)
        latest_close = float(close[-1])
        
        # 2. Scoring Logic (0-100)
        score = 50 # Start neutral
        
        # RSI Score
        if latest_rsi < 30:
            score += 15
        elif latest_rsi > 70:
            score -= 15
            
        # MACD Score
        if latest_macd_diff > 0:
            score += 10
        else:
            score -= 10
            
        # KDJ Score
        if latest_k < 20:
             score += 10
        elif latest_k > 80:
             score -= 10
             
        # MA Trend
        if latest_ma5 > latest_ma20:
            score += 10
        else:
            score -= 10
            
        # Bollinger
        if latest_close < latest_bb_low:
            score += 5 
        elif latest_close > latest_bb_high:
            score -= 5

        score = max(0, min(100, score))
        
        # 3. Determine Signal
        if score >= 80:
            signal = "STRONG_BUY"
        elif score >= 60:
            signal = "BUY"
        elif score <= 20:
            signal = "STRONG_SELL"
        elif score <= 40:
            signal = "SELL"
        else:
            signal = "HOLD"
            
        indicators = {
            "RSI": latest_rsi,
            "MACD": latest_macd,
            "MACD_Signal": latest_macd_signal,
            "KDJ_K": latest_k,
            "KDJ_D": latest_d,
            "KDJ_J": latest_j,
            "MA5": latest_ma5,
            "MA20": latest_ma20,
            "BB_High": latest_bb_high,
            "BB_Low": latest_bb_low,
            "Close": latest_close
        }
        
        return AnalysisResult(
            score=score,
            summary=f"Technical Score (TA-Lib): {score}/100. Trend detected.",
            indicators=indicators,
            signal=signal
        )
