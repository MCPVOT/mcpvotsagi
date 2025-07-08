#!/usr/bin/env python3
"""
Finnhub API Integration
=======================
Complete integration with Finnhub for financial data
"""

import os
import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import pandas as pd
import numpy as np
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FinnhubIntegration")


@dataclass 
class MarketQuote:
    """Market quote data"""
    symbol: str
    current_price: float
    high: float
    low: float
    open: float
    previous_close: float
    timestamp: datetime
    

@dataclass
class CompanyNews:
    """Company news item"""
    headline: str
    summary: str
    source: str
    url: str
    datetime: datetime
    sentiment: Optional[float] = None
    

class FinnhubClient:
    """Complete Finnhub API client"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FINNHUB_API_KEY")
        if not self.api_key:
            raise ValueError("Finnhub API key required")
            
        self.base_url = "https://finnhub.io/api/v1"
        self.websocket_url = "wss://ws.finnhub.io"
        
        # Rate limiting
        self.rate_limit = 60  # 60 requests per minute
        self.request_times = deque(maxlen=self.rate_limit)
        
        # Cache
        self.cache = {}
        self.cache_ttl = 60  # 60 seconds
        
    async def _rate_limit_check(self):
        """Check and enforce rate limits"""
        now = datetime.now()
        
        # Remove old requests
        while self.request_times and (now - self.request_times[0]).seconds > 60:
            self.request_times.popleft()
            
        # Check if we're at limit
        if len(self.request_times) >= self.rate_limit:
            sleep_time = 60 - (now - self.request_times[0]).seconds
            if sleep_time > 0:
                logger.warning(f"Rate limit reached, sleeping {sleep_time}s")
                await asyncio.sleep(sleep_time)
                
        self.request_times.append(now)
        
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make API request with rate limiting and caching"""
        
        # Check cache
        cache_key = f"{endpoint}_{json.dumps(params or {})}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if (datetime.now() - cached_time).seconds < self.cache_ttl:
                return cached_data
                
        # Rate limit check
        await self._rate_limit_check()
        
        # Make request
        params = params or {}
        params["token"] = self.api_key
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}{endpoint}",
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Cache result
                        self.cache[cache_key] = (data, datetime.now())
                        
                        return data
                    else:
                        logger.error(f"API error: {response.status}")
                        return {}
                        
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {}
            
    async def get_quote(self, symbol: str) -> Optional[MarketQuote]:
        """Get real-time quote for symbol"""
        
        data = await self._make_request("/quote", {"symbol": symbol})
        
        if data:
            return MarketQuote(
                symbol=symbol,
                current_price=data.get("c", 0),
                high=data.get("h", 0),
                low=data.get("l", 0),
                open=data.get("o", 0),
                previous_close=data.get("pc", 0),
                timestamp=datetime.fromtimestamp(data.get("t", 0))
            )
            
        return None
        
    async def get_company_news(self, 
                             symbol: str,
                             from_date: Optional[str] = None,
                             to_date: Optional[str] = None) -> List[CompanyNews]:
        """Get company news"""
        
        if not from_date:
            from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
            
        data = await self._make_request(
            "/company-news",
            {
                "symbol": symbol,
                "from": from_date,
                "to": to_date
            }
        )
        
        news_items = []
        for item in data:
            news_items.append(CompanyNews(
                headline=item.get("headline", ""),
                summary=item.get("summary", ""),
                source=item.get("source", ""),
                url=item.get("url", ""),
                datetime=datetime.fromtimestamp(item.get("datetime", 0))
            ))
            
        return news_items
        
    async def get_financials(self, symbol: str, statement: str = "bs") -> Dict[str, Any]:
        """Get financial statements
        
        Args:
            symbol: Stock symbol
            statement: Type of statement (bs=balance sheet, ic=income, cf=cash flow)
        """
        
        data = await self._make_request(
            "/stock/financials-reported",
            {
                "symbol": symbol,
                "freq": "quarterly"
            }
        )
        
        return data
        
    async def get_technical_indicators(self, 
                                     symbol: str,
                                     resolution: str = "D",
                                     indicator: str = "sma") -> Dict[str, Any]:
        """Get technical indicators"""
        
        # Get candle data first
        to_timestamp = int(datetime.now().timestamp())
        from_timestamp = to_timestamp - (365 * 24 * 60 * 60)  # 1 year
        
        candles = await self._make_request(
            "/stock/candle",
            {
                "symbol": symbol,
                "resolution": resolution,
                "from": from_timestamp,
                "to": to_timestamp
            }
        )
        
        if not candles or candles.get("s") != "ok":
            return {}
            
        # Calculate indicators
        closes = candles.get("c", [])
        
        indicators = {
            "sma_20": self._calculate_sma(closes, 20),
            "sma_50": self._calculate_sma(closes, 50),
            "rsi": self._calculate_rsi(closes),
            "macd": self._calculate_macd(closes)
        }
        
        return indicators
        
    async def get_insider_transactions(self, symbol: str) -> List[Dict[str, Any]]:
        """Get insider transactions"""
        
        data = await self._make_request(
            "/stock/insider-transactions",
            {"symbol": symbol}
        )
        
        return data.get("data", [])
        
    async def get_earnings_calendar(self, 
                                  from_date: Optional[str] = None,
                                  to_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get earnings calendar"""
        
        if not from_date:
            from_date = datetime.now().strftime("%Y-%m-%d")
        if not to_date:
            to_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            
        data = await self._make_request(
            "/calendar/earnings",
            {
                "from": from_date,
                "to": to_date
            }
        )
        
        return data.get("earningsCalendar", [])
        
    async def get_market_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Get market sentiment data"""
        
        # Social sentiment
        social = await self._make_request(
            "/stock/social-sentiment",
            {"symbol": symbol}
        )
        
        # Recommendation trends
        recommendations = await self._make_request(
            "/stock/recommendation",
            {"symbol": symbol}
        )
        
        # Price target
        price_target = await self._make_request(
            "/stock/price-target",
            {"symbol": symbol}
        )
        
        return {
            "social_sentiment": social,
            "recommendations": recommendations,
            "price_target": price_target
        }
        
    async def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        """Search for symbols"""
        
        data = await self._make_request(
            "/search",
            {"q": query}
        )
        
        return data.get("result", [])
        
    def _calculate_sma(self, prices: List[float], period: int) -> Optional[float]:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return None
            
        return sum(prices[-period:]) / period
        
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> Optional[float]:
        """Calculate RSI"""
        if len(prices) < period + 1:
            return None
            
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
        
    def _calculate_macd(self, prices: List[float]) -> Dict[str, Optional[float]]:
        """Calculate MACD"""
        if len(prices) < 26:
            return {"macd": None, "signal": None, "histogram": None}
            
        # Calculate EMAs
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        
        if ema_12 is None or ema_26 is None:
            return {"macd": None, "signal": None, "histogram": None}
            
        macd = ema_12 - ema_26
        
        # Signal line (9-day EMA of MACD)
        # Simplified calculation
        signal = macd * 0.9  # Placeholder
        
        histogram = macd - signal
        
        return {
            "macd": macd,
            "signal": signal,
            "histogram": histogram
        }
        
    def _calculate_ema(self, prices: List[float], period: int) -> Optional[float]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return None
            
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
            
        return ema


class FinnhubWebSocketClient:
    """WebSocket client for real-time data"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = f"wss://ws.finnhub.io?token={api_key}"
        self.subscriptions = set()
        self.callbacks = {}
        
    async def connect(self):
        """Connect to WebSocket"""
        import websockets
        
        self.ws = await websockets.connect(self.url)
        logger.info("Connected to Finnhub WebSocket")
        
        # Start listening
        asyncio.create_task(self._listen())
        
    async def subscribe(self, symbol: str, callback):
        """Subscribe to symbol updates"""
        self.subscriptions.add(symbol)
        self.callbacks[symbol] = callback
        
        await self.ws.send(json.dumps({
            "type": "subscribe",
            "symbol": symbol
        }))
        
    async def unsubscribe(self, symbol: str):
        """Unsubscribe from symbol"""
        self.subscriptions.discard(symbol)
        
        await self.ws.send(json.dumps({
            "type": "unsubscribe", 
            "symbol": symbol
        }))
        
    async def _listen(self):
        """Listen for WebSocket messages"""
        async for message in self.ws:
            try:
                data = json.loads(message)
                
                if data.get("type") == "trade":
                    for trade in data.get("data", []):
                        symbol = trade.get("s")
                        if symbol in self.callbacks:
                            await self.callbacks[symbol](trade)
                            
            except Exception as e:
                logger.error(f"WebSocket error: {e}")


# Integration with TradingAgents
class FinnhubTradingAgentsAdapter:
    """Adapter to integrate Finnhub with TradingAgents"""
    
    def __init__(self, finnhub_client: FinnhubClient):
        self.finnhub = finnhub_client
        
    async def get_data_for_trading_agents(self, ticker: str, date: str) -> Dict[str, Any]:
        """Get data formatted for TradingAgents"""
        
        # Get all relevant data
        quote = await self.finnhub.get_quote(ticker)
        news = await self.finnhub.get_company_news(ticker)
        technicals = await self.finnhub.get_technical_indicators(ticker)
        sentiment = await self.finnhub.get_market_sentiment(ticker)
        
        # Format for TradingAgents
        return {
            "ticker": ticker,
            "date": date,
            "price_data": {
                "current": quote.current_price if quote else 0,
                "high": quote.high if quote else 0,
                "low": quote.low if quote else 0,
                "open": quote.open if quote else 0,
                "close": quote.previous_close if quote else 0
            },
            "technical_indicators": technicals,
            "news": [
                {
                    "headline": n.headline,
                    "summary": n.summary,
                    "datetime": n.datetime.isoformat()
                }
                for n in news[:10]  # Limit to 10 most recent
            ],
            "sentiment": sentiment
        }


async def main():
    """Test Finnhub integration"""
    
    client = FinnhubClient()
    
    # Test quote
    quote = await client.get_quote("AAPL")
    if quote:
        print(f"AAPL Price: ${quote.current_price}")
        
    # Test news
    news = await client.get_company_news("AAPL")
    print(f"Found {len(news)} news items")
    
    # Test technical indicators
    technicals = await client.get_technical_indicators("AAPL")
    print(f"Technical indicators: {technicals}")
    
    # Test sentiment
    sentiment = await client.get_market_sentiment("AAPL")
    print(f"Sentiment data available: {bool(sentiment)}")


if __name__ == "__main__":
    asyncio.run(main())