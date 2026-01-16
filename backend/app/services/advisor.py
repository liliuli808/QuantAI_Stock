from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class AdviceResult:
    action: str
    entry_point: Optional[float] = None
    exit_point: Optional[float] = None
    rationale: str = ""

class InvestmentAdvisor:
    def generate_advice(self, current_price: float, tech_score: float, sentiment_score: float, 
                       holding_cost: Optional[float] = None) -> AdviceResult:
        """
        Generate trading advice based on scores and user state (holding or not).
        Composite Score = 40% Technical + 30% Sentiment + 30% Trend(implicit in tech)
        Actually requirement says:
        1. Tech (40%)
        2. Sentiment (30%)
        3. Advice (20%) - output
        4. Summary (10%)
        
        But for generating advice we use inputs: Tech Score and Sentiment Score.
        Let's assume a composite alpha score.
        """
        
        # Calculate composite alpha (0-100)
        # Using 60% tech, 40% sentiment for simplicity of advice generation
        alpha = (tech_score * 0.6) + (sentiment_score * 0.4)
        
        action = "HOLD"
        entry = None
        exit_val = None
        rationale = f"Composite Score: {alpha:.1f}. "
        
        if holding_cost:
            # User is HOLDING
            profit_pct = (current_price - holding_cost) / holding_cost
            
            if alpha > 75:
                action = "ADD POSITION" if profit_pct > 0 else "HOLD/AVERAGE DOWN"
                rationale += "Strong signals suggest upside. Consider increasing exposure."
            elif alpha < 30:
                action = "SELL/CUT LOSS"
                rationale += "Weak signals detected. Protect capital."
                exit_val = current_price * 0.99 # Immediate exit suggestion
            elif alpha > 50:
                action = "HOLD"
                rationale += "Neutral to positive outlook. Continue holding."
                exit_val = current_price * 1.15 # Target
            else:
                action = "REDUCE"
                rationale += "Outlook weakening. Consider taking partial profits."
                
        else:
            # User is PLANNING TO ENTER
            if alpha > 70:
                action = "BUY"
                entry = current_price * 1.005 # Just above market
                exit_val = current_price * 1.10 # 10% target
                rationale += "Strong buy signal. Good entry point detected."
            elif alpha > 50:
                action = "WATCH"
                entry = current_price * 0.98 # Wait for dip
                rationale += "Positive but wait for better entry."
            else:
                action = "AVOID"
                rationale += "Technical/Sentiment mix is weak. Not recommended."
                
        return AdviceResult(
            action=action,
            entry_point=entry,
            exit_point=exit_val,
            rationale=rationale
        )
