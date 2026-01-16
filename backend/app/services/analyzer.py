import pandas as pd
import ta
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class AnalysisResult:
    score: float
    summary: str
    indicators: Dict[str, Any]
    signal: str # "BUY", "SELL", "HOLD", "STRONG_BUY", "STRONG_SELL"

class TechnicalAnalyzer:
    def analyze(self, df: pd.DataFrame) -> AnalysisResult:
        """
        Perform comprehensive technical analysis on the dataframe.
        Expects columns: Open, High, Low, Close, Volume
        """
        if df.empty:
            return AnalysisResult(0, "No data", {}, "HOLD")

        # 1. Calculate Indicators
        # MACD
        macd = ta.trend.MACD(close=df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()
        df['MACD_diff'] = macd.macd_diff()

        # RSI
        rsi = ta.momentum.RSIIndicator(close=df['Close'])
        df['RSI'] = rsi.rsi()

        # KDJ (Stochastic Oscillator)
        stoch = ta.momentum.StochasticOscillator(high=df['High'], low=df['Low'], close=df['Close'])
        df['K'] = stoch.stoch()
        df['D'] = stoch.stoch_signal()
        # "J" is typically 3*K - 2*D
        df['J'] = 3 * df['K'] - 2 * df['D']

        # Bollinger Bands
        bb = ta.volatility.BollingerBands(close=df['Close'])
        df['BB_high'] = bb.bollinger_hband()
        df['BB_low'] = bb.bollinger_lband()
        df['BB_avg'] = bb.bollinger_mavg()

        # MA (Moving Averages)
        df['MA5'] = ta.trend.SMAIndicator(close=df['Close'], window=5).sma_indicator()
        df['MA20'] = ta.trend.SMAIndicator(close=df['Close'], window=20).sma_indicator()
        
        # Get latest values
        latest = df.iloc[-1]
        
        # 2. Scoring Logic (0-100)
        score = 50 # Start neutral
        
        # RSI Score
        # Optimal: 30-70. <30 Oversold (Bullish), >70 Overbought (Bearish)
        if latest['RSI'] < 30:
            score += 15
        elif latest['RSI'] > 70:
            score -= 15
            
        # MACD Score
        # Golden Cross (Diff > 0 and crossing up) - simplified checking if Diff > 0
        if latest['MACD_diff'] > 0:
            score += 10
        else:
            score -= 10
            
        # KDJ Score
        # J < 0 or K < 20 (Oversold), J > 100 or K > 80 (Overbought)
        if latest['K'] < 20:
             score += 10
        elif latest['K'] > 80:
             score -= 10
             
        # MA Trend
        if latest['MA5'] > latest['MA20']:
            score += 10 # Bullish trend
        else:
            score -= 10
            
        # Bollinger
        if latest['Close'] < latest['BB_low']:
            score += 5 # Rebound potential
        elif latest['Close'] > latest['BB_high']:
            score -= 5 # Pullback risk

        # Clamp score
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
            "RSI": latest['RSI'],
            "MACD": latest['MACD'],
            "MACD_Signal": latest['MACD_signal'],
            "KDJ_K": latest['K'],
            "KDJ_D": latest['D'],
            "KDJ_J": latest['J'],
            "MA5": latest['MA5'],
            "MA20": latest['MA20'],
            "BB_High": latest['BB_high'],
            "BB_Low": latest['BB_low'],
            "Close": latest['Close']
        }
        
        return AnalysisResult(
            score=score,
            summary=f"Technical Score: {score}/100. Trend detected.",
            indicators=indicators,
            signal=signal
        )
