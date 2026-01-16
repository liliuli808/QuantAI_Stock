from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any

class StockRequest(BaseModel):
    stock_code: str = Field(..., description="Stock ticker symbol (e.g., AAPL, 0700.HK)")
    holding_cost: Optional[float] = Field(None, description="Average holding cost if user has position")

    @validator('stock_code')
    def validate_stock_code(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError('Invalid stock code')
        # Basic regex can be added here if needed, but keeping it flexible for now
        return v.upper()

    @validator('holding_cost')
    def validate_holding_cost(cls, v):
        if v is not None and v < 0:
            raise ValueError('Holding cost must be non-negative')
        return v

class AnalysisResponse(BaseModel):
    ticker: str
    current_price: float
    analysis_date: str
    
    # 1. Technical
    tech_score: float
    tech_signal: str
    indicators: Dict[str, Any]
    
    # 2. Sentiment
    sentiment_score: float
    sentiment_summary: str
    news_headlines: List[str]
    
    # 3. Advice
    advice_action: str
    advice_rationale: str
    entry_point: Optional[float]
    exit_point: Optional[float]
    
    # 4. Summary
    overall_score: float # Computed or passed
    summary_text: str

class ReportRequest(BaseModel):
    analysis_data: AnalysisResponse
    language: str = "en" # 'en' or 'zh'
