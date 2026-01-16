from textblob import TextBlob
import random
from typing import Dict, Any

class SentimentAnalyzer:
    def analyze(self, ticker: str) -> Dict[str, Any]:
        """
        Mock sentiment analysis. 
        In a real app, this would fetch news for the ticker and run NLP.
        """
        # Mocking generic news headlines
        mock_news = [
            f"{ticker} announces new product line.",
            f"Analysts upgrade {ticker} rating.",
            f"Market volatility affects {ticker}.",
            f"{ticker} quarterly earnings beat expectations."
        ]
        
        # Simple analysis simulation using random for variation but weighted slightly positive for demo
        # We can also use TextBlob on the mock headlines
        
        polarity_sum = 0
        for news in mock_news:
            blob = TextBlob(news)
            polarity_sum += blob.sentiment.polarity
            
        avg_polarity = polarity_sum / len(mock_news)
        
        # Add some random noise to simulate dynamic data
        avg_polarity += (random.random() - 0.5) * 0.2
        
        # Scale to 0-100 score for consistency (0 is very negative, 50 neutral, 100 very positive)
        # Polarity is -1 to 1.
        sentiment_score = (avg_polarity + 1) * 50
        sentiment_score = max(0, min(100, sentiment_score))
        
        return {
            "score": sentiment_score,
            "headlines": mock_news,
            "summary": "Positive market sentiment detected." if sentiment_score > 55 else "Mixed/Neutral sentiment."
        }
