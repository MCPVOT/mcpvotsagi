#!/usr/bin/env python3
"""
Real-Time Market Data Collector
==============================
Collects real market data from multiple sources
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime
from pathlib import Path
import yfinance as yf
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MarketDataCollector")

class RealTimeMarketDataCollector:
    def __init__(self):
        self.f_drive_root = Path("F:/MCPVotsAGI_Data")
        self.market_data_path = self.f_drive_root / "market_data"
        self.market_data_path.mkdir(parents=True, exist_ok=True)
        
        # Precious metals ETFs
        self.symbols = {
            'precious_metals': ['GLD', 'SLV', 'PPLT', 'PALL'],
            'crypto': ['BTC-USD', 'ETH-USD', 'SOL-USD'],
            'indices': ['^GSPC', '^DJI', '^IXIC', '^VIX']
        }
        
        # Data sources
        self.sources = {
            'yahoo': self._fetch_yahoo_data,
            'alphavantage': self._fetch_alphavantage_data,
            'cryptocompare': self._fetch_crypto_data
        }
        
    async def _fetch_yahoo_data(self, symbol: str) -> dict:
        """Fetch data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get real-time quote
            info = ticker.info
            history = ticker.history(period="1d", interval="1m")
            
            if not history.empty:
                latest = history.iloc[-1]
                
                return {
                    'symbol': symbol,
                    'price': float(latest['Close']),
                    'open': float(latest['Open']),
                    'high': float(latest['High']),
                    'low': float(latest['Low']),
                    'volume': int(latest['Volume']),
                    'timestamp': history.index[-1].timestamp(),
                    'bid': info.get('bid', latest['Close']),
                    'ask': info.get('ask', latest['Close']),
                    'spread': info.get('ask', latest['Close']) - info.get('bid', latest['Close']),
                    'change_percent': info.get('regularMarketChangePercent', 0),
                    'day_high': info.get('dayHigh', latest['High']),
                    'day_low': info.get('dayLow', latest['Low']),
                    'market_cap': info.get('marketCap', 0),
                    'pe_ratio': info.get('trailingPE', 0)
                }
                
        except Exception as e:
            logger.error(f"Yahoo Finance error for {symbol}: {e}")
            
        return None
        
    async def _fetch_alphavantage_data(self, symbol: str) -> dict:
        """Fetch data from Alpha Vantage API"""
        # Requires API key - implement if available
        api_key = os.environ.get('ALPHAVANTAGE_API_KEY')
        if not api_key:
            return None
            
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://www.alphavantage.co/query"
                params = {
                    'function': 'GLOBAL_QUOTE',
                    'symbol': symbol,
                    'apikey': api_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        quote = data.get('Global Quote', {})
                        
                        if quote:
                            return {
                                'symbol': symbol,
                                'price': float(quote['05. price']),
                                'open': float(quote['02. open']),
                                'high': float(quote['03. high']),
                                'low': float(quote['04. low']),
                                'volume': int(quote['06. volume']),
                                'change_percent': float(quote['10. change percent'].rstrip('%')),
                                'timestamp': time.time()
                            }
                            
        except Exception as e:
            logger.error(f"Alpha Vantage error for {symbol}: {e}")
            
        return None
        
    async def _fetch_crypto_data(self, symbol: str) -> dict:
        """Fetch cryptocurrency data"""
        if not symbol.endswith('-USD'):
            return None
            
        crypto_symbol = symbol.replace('-USD', '')
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.coinbase.com/v2/exchange-rates?currency={crypto_symbol}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        rates = data['data']['rates']
                        
                        return {
                            'symbol': symbol,
                            'price': float(rates['USD']),
                            'timestamp': time.time()
                        }
                        
        except Exception as e:
            logger.error(f"Crypto data error for {symbol}: {e}")
            
        return None
        
    async def collect_all_data(self):
        """Collect data for all symbols"""
        all_symbols = []
        for category, symbols in self.symbols.items():
            all_symbols.extend(symbols)
            
        results = []
        
        for symbol in all_symbols:
            # Try Yahoo Finance first
            data = await self._fetch_yahoo_data(symbol)
            
            # Fallback to other sources if needed
            if not data and symbol.endswith('-USD'):
                data = await self._fetch_crypto_data(symbol)
                
            if data:
                results.append(data)
                
                # Store individual symbol data
                symbol_file = self.market_data_path / "realtime" / f"{symbol}.json"
                symbol_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(symbol_file, 'w') as f:
                    json.dump(data, f)
                    
                logger.info(f"Collected data for {symbol}: ${data['price']:.2f}")
                
        # Store aggregated data
        if results:
            aggregate_file = self.market_data_path / "realtime" / "latest_all.json"
            with open(aggregate_file, 'w') as f:
                json.dump({
                    'timestamp': time.time(),
                    'data': results
                }, f)
                
        return results
        
    async def run_continuous_collection(self):
        """Run continuous data collection"""
        logger.info("Starting real-time market data collection...")
        
        while True:
            try:
                await self.collect_all_data()
                
                # During market hours, collect every 30 seconds
                # Outside market hours, collect every 5 minutes
                now = datetime.now()
                if 9 <= now.hour < 16 and now.weekday() < 5:  # Market hours
                    await asyncio.sleep(30)
                else:
                    await asyncio.sleep(300)
                    
            except Exception as e:
                logger.error(f"Collection cycle error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

if __name__ == "__main__":
    collector = RealTimeMarketDataCollector()
    asyncio.run(collector.run_continuous_collection())
