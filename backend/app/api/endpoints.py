from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from app.models.schemas import StockRequest, AnalysisResponse, ReportRequest
from app.services.data_fetcher import YFinanceFetcher, StockDataFetcher
from app.services.analyzer import TechnicalAnalyzer
from app.services.sentiment import SentimentAnalyzer
from app.services.advisor import InvestmentAdvisor
from fastapi.responses import HTMLResponse, Response
from app.services.report_generator import report_generator
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# ... (dependency injection code is unchanged)


# Dependency injection for services
def get_data_fetcher():
    return YFinanceFetcher()

def get_analyzer():
    return TechnicalAnalyzer()

def get_sentiment_analyzer():
    return SentimentAnalyzer()

def get_advisor():
    return InvestmentAdvisor()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_stock(
    request: StockRequest,
    fetcher: StockDataFetcher = Depends(get_data_fetcher),
    tech_analyzer: TechnicalAnalyzer = Depends(get_analyzer),
    sentiment_analyzer: SentimentAnalyzer = Depends(get_sentiment_analyzer),
    advisor: InvestmentAdvisor = Depends(get_advisor)
):
    try:
        # 1. Fetch Data
        df = fetcher.fetch_history(request.stock_code)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {request.stock_code}")
            
        current_price = fetcher.get_current_price(request.stock_code)
        
        # 2. Technical Analysis
        tech_result = tech_analyzer.analyze(df)
        
        # 3. Sentiment Analysis
        sentiment_result = sentiment_analyzer.analyze(request.stock_code)
        
        # 4. Generate Advice
        advice = advisor.generate_advice(
            current_price=current_price,
            tech_score=tech_result.score,
            sentiment_score=sentiment_result['score'],
            holding_cost=request.holding_cost
        )
        
        # 5. Construct Response
        overall_score = (tech_result.score * 0.4) + (sentiment_result['score'] * 0.3) + (20) # +20 base/mock for advice component? 
        # Actually let's just use weighted average logic
        # 40% Tech, 30% Sentiment, 20% Advice (Action Strength?), 10% Summary
        # We'll simplify to just returning the components and let frontend display or normalized score
        
        return AnalysisResponse(
            ticker=request.stock_code,
            current_price=current_price,
            analysis_date=datetime.now().isoformat(),
            
            tech_score=tech_result.score,
            tech_signal=tech_result.signal,
            indicators=tech_result.indicators,
            
            sentiment_score=sentiment_result['score'],
            sentiment_summary=sentiment_result['summary'],
            news_headlines=sentiment_result['headlines'],
            
            advice_action=advice.action,
            advice_rationale=advice.rationale,
            entry_point=advice.entry_point,
            exit_point=advice.exit_point,
            
            overall_score=overall_score, # Placeholder calculation
            summary_text=f"Analysis complete for {request.stock_code}. {advice.action} recommendation."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
from fastapi.responses import HTMLResponse, Response
from app.services.report_generator import report_generator

@router.post("/report/html", response_class=HTMLResponse)
async def generate_html_report(request: ReportRequest):
    return report_generator.generate_html(request.analysis_data)

@router.post("/report/pdf")
async def generate_pdf_report(request: ReportRequest):
    pdf_bytes = report_generator.generate_pdf(request.analysis_data)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=report_{request.analysis_data.ticker}.pdf"
    })
