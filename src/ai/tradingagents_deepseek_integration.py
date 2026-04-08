#!/usr/bin/env python3
"""
TradingAgents + DeepSeek-R1 + Claude Code Integration
=====================================================
Combines TradingAgents framework with DeepSeek-R1 (via Ollama) and Claude Code
for making the hardest trading decisions.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Optional, List, Tuple
from datetime import datetime
from pathlib import Path

# Add TradingAgents to path
sys.path.append(str(Path(__file__).parent / "TradingAgents"))

try:
    import httpx
    import ollama
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    from tradingagents.default_config import DEFAULT_CONFIG
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx", "ollama"])
    
    # Try imports again
    import httpx
    import ollama
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    from tradingagents.default_config import DEFAULT_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeepSeekTradingBrain:
    """DeepSeek-R1 integration for complex trading decisions"""
    
    def __init__(self, model_name: str = "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL"):
        self.model_name = model_name
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        
    async def analyze_complex_decision(self, 
                                     ticker: str,
                                     market_data: dict[str, Any],
                                     analyst_reports: dict[str, Any]) -> dict[str, Any]:
        """Use DeepSeek-R1 for complex reasoning about trading decisions"""
        
        prompt = f"""You are DeepSeek-R1, specialized in making the hardest trading decisions.
        
Analyze this trading scenario for {ticker}:

Market Data:
{json.dumps(market_data, indent=2)}

Analyst Reports:
{json.dumps(analyst_reports, indent=2)}

Provide a comprehensive analysis considering:
1. Hidden market risks not obvious in the data
2. Complex correlations between different factors
3. Potential black swan events
4. Game theory aspects of market movements
5. Your confidence level and reasoning chain

Output as JSON with structure:
{{
    "decision": "BUY/SELL/HOLD",
    "confidence": 0.0-1.0,
    "reasoning_chain": ["step1", "step2", ...],
    "hidden_risks": ["risk1", "risk2", ...],
    "opportunity_score": 0.0-1.0,
    "recommended_position_size": 0.0-1.0
}}
"""
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                format="json"
            )
            
            return json.loads(response['message']['content'])
            
        except Exception as e:
            logger.error(f"DeepSeek analysis failed: {e}")
            return {
                "decision": "HOLD",
                "confidence": 0.0,
                "reasoning_chain": ["Error in analysis"],
                "hidden_risks": ["Analysis failed"],
                "opportunity_score": 0.0,
                "recommended_position_size": 0.0
            }


class ClaudeCodeTradingAdvisor:
    """Claude Code (Opus 4) integration via MCP"""
    
    def __init__(self):
        self.mcp_memory_port = int(os.getenv("MCP_MEMORY_PORT", "3002"))
        self.base_url = f"http://localhost:{self.mcp_memory_port}"
        
    async def get_strategic_advice(self,
                                 ticker: str,
                                 market_context: dict[str, Any],
                                 deepseek_analysis: dict[str, Any]) -> dict[str, Any]:
        """Get strategic trading advice from Claude Code"""
        
        # In real implementation, this would connect to Claude via MCP
        # For now, we'll simulate the response structure
        
        advice = {
            "strategy": "momentum_based",
            "timeframe": "medium_term",
            "entry_points": [],
            "exit_strategy": {
                "take_profit": 0.15,  # 15% profit target
                "stop_loss": 0.05     # 5% stop loss
            },
            "portfolio_allocation": 0.05,  # 5% of portfolio
            "hedging_recommendations": [],
            "market_regime": "bullish_momentum"
        }
        
        # Adjust based on DeepSeek's analysis
        if deepseek_analysis.get("confidence", 0) < 0.3:
            advice["portfolio_allocation"] *= 0.5
            advice["exit_strategy"]["stop_loss"] = 0.03
            
        return advice


class TradingDecisionEngine:
    """Main integration engine combining all components"""
    
    def __init__(self, 
                 use_claude: bool = True,
                 use_deepseek: bool = True,
                 ollama_model: Optional[str] = None):
        
        # Initialize TradingAgents
        self.config = DEFAULT_CONFIG.copy()
        self.config["online_tools"] = True  # Use real-time data
        self.ta_graph = TradingAgentsGraph(debug=True, config=self.config)
        
        # Initialize AI components
        self.use_deepseek = use_deepseek
        self.use_claude = use_claude
        
        if self.use_deepseek:
            model = ollama_model or "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL"
            self.deepseek = DeepSeekTradingBrain(model)
            
        if self.use_claude:
            self.claude = ClaudeCodeTradingAdvisor()
            
        self.decision_history = []
        
    async def analyze_and_decide(self,
                               ticker: str,
                               date: str,
                               risk_tolerance: str = "moderate") -> dict[str, Any]:
        """Main decision-making pipeline"""
        
        logger.info(f"Analyzing {ticker} for {date} with {risk_tolerance} risk tolerance")
        
        # Step 1: Get TradingAgents analysis
        logger.info("Running TradingAgents multi-agent analysis...")
        ta_state, ta_decision = self.ta_graph.propagate(ticker, date)
        
        # Extract key information
        market_data = {
            "ticker": ticker,
            "date": date,
            "technical_indicators": ta_state.get("technical_analysis", {}),
            "fundamental_data": ta_state.get("fundamental_analysis", {}),
            "sentiment_score": ta_state.get("sentiment_analysis", {}).get("score", 0),
            "news_impact": ta_state.get("news_analysis", {})
        }
        
        analyst_reports = {
            "technical": ta_state.get("technical_analyst_report", ""),
            "fundamental": ta_state.get("fundamental_analyst_report", ""),
            "sentiment": ta_state.get("sentiment_analyst_report", ""),
            "news": ta_state.get("news_analyst_report", "")
        }
        
        # Step 2: DeepSeek complex analysis
        deepseek_analysis = {"decision": "HOLD", "confidence": 0.5}
        if self.use_deepseek:
            logger.info("Running DeepSeek-R1 complex reasoning...")
            deepseek_analysis = await self.deepseek.analyze_complex_decision(
                ticker, market_data, analyst_reports
            )
        
        # Step 3: Claude strategic advice
        claude_advice = {"strategy": "default", "portfolio_allocation": 0.05}
        if self.use_claude:
            logger.info("Getting Claude Code strategic advice...")
            claude_advice = await self.claude.get_strategic_advice(
                ticker, market_data, deepseek_analysis
            )
        
        # Step 4: Combine all inputs for final decision
        final_decision = self._combine_decisions(
            ta_decision,
            deepseek_analysis,
            claude_advice,
            risk_tolerance
        )
        
        # Step 5: Log decision
        decision_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "ticker": ticker,
            "date": date,
            "trading_agents_decision": ta_decision,
            "deepseek_analysis": deepseek_analysis,
            "claude_advice": claude_advice,
            "final_decision": final_decision
        }
        
        self.decision_history.append(decision_record)
        
        # Save to file for audit
        self._save_decision_log(decision_record)
        
        return final_decision
        
    def _combine_decisions(self,
                          ta_decision: dict[str, Any],
                          deepseek_analysis: dict[str, Any],
                          claude_advice: dict[str, Any],
                          risk_tolerance: str) -> dict[str, Any]:
        """Combine all AI decisions into final trading decision"""
        
        # Extract decisions
        ta_action = ta_decision.get("action", "HOLD")
        ds_action = deepseek_analysis.get("decision", "HOLD")
        ds_confidence = deepseek_analysis.get("confidence", 0.5)
        
        # Voting mechanism
        votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
        
        # TradingAgents vote
        votes[ta_action] += 1
        
        # DeepSeek weighted vote based on confidence
        votes[ds_action] += ds_confidence
        
        # Determine action
        final_action = max(votes, key=votes.get)
        
        # Adjust position size based on consensus and risk
        base_position = claude_advice.get("portfolio_allocation", 0.05)
        
        if risk_tolerance == "conservative":
            base_position *= 0.5
        elif risk_tolerance == "aggressive":
            base_position *= 1.5
            
        # Reduce position if no strong consensus
        consensus_strength = votes[final_action] / sum(votes.values())
        if consensus_strength < 0.6:
            base_position *= 0.7
            
        return {
            "action": final_action,
            "position_size": min(base_position, 0.1),  # Max 10% position
            "confidence": consensus_strength,
            "entry_strategy": claude_advice.get("entry_points", []),
            "exit_strategy": claude_advice.get("exit_strategy", {}),
            "risk_factors": deepseek_analysis.get("hidden_risks", []),
            "reasoning": {
                "trading_agents": ta_decision.get("reasoning", ""),
                "deepseek_chain": deepseek_analysis.get("reasoning_chain", []),
                "strategy": claude_advice.get("strategy", "")
            }
        }
        
    def _save_decision_log(self, decision: dict[str, Any]):
        """Save decision to audit log"""
        log_dir = Path("trading_decisions")
        log_dir.mkdir(exist_ok=True)
        
        filename = f"{decision['ticker']}_{decision['date']}_{decision['timestamp']}.json"
        filepath = log_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(decision, f, indent=2)
            
        logger.info(f"Decision logged to {filepath}")


async def main():
    """Example usage"""
    
    # Initialize the trading decision engine
    engine = TradingDecisionEngine(
        use_claude=True,
        use_deepseek=True,
        ollama_model="hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL"
    )
    
    # Make a trading decision
    decision = await engine.analyze_and_decide(
        ticker="NVDA",
        date="2025-01-03",
        risk_tolerance="moderate"
    )
    
    print("\n" + "="*60)
    print("FINAL TRADING DECISION")
    print("="*60)
    print(f"Action: {decision['action']}")
    print(f"Position Size: {decision['position_size']*100:.1f}% of portfolio")
    print(f"Confidence: {decision['confidence']*100:.1f}%")
    print(f"Risk Factors: {', '.join(decision['risk_factors'][:3])}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())