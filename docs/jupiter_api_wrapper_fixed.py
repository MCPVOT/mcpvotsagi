#!/usr/bin/env python3
"""
Jupiter API Wrapper V3 - Enhanced with Fixed Token Addresses
===========================================================
Complete Jupiter DEX API integration with proper Solana token mint addresses
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import time
import hashlib
from dataclasses import dataclass
from enum import Enum
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JupiterAPI")

# SOLANA TOKEN MINT ADDRESSES (Real addresses from Solana mainnet)
SOLANA_TOKEN_MINTS = {
    "SOL": "So11111111111111111111111111111111111111112",  # Wrapped SOL
    "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USD Coin
    "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # Tether
    "BTC": "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E",  # Bitcoin (Wormhole)
    "ETH": "2FPyTwcZLUg1MDrwsyoP4D6s1tM7hAkHYRjkNb5w6Pxk",  # Ethereum (Wormhole)
    "RAY": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",  # Raydium
    "JUP": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",  # Jupiter
    "ORCA": "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE",  # Orca
    "SRM": "SRMuApVNdxXokk5GT7XD5cUUgXMBCoAz2LHeuAoKWRt",  # Serum
    "STEP": "StepAscQoEioFxxWGnh2sLBDFp9d8rvKz2Yp39iDpyT",  # Step Finance
    "ATLAS": "ATLASXmbPQxBUYbxPsV97usA3fPQYEqzQBUHgiFCUsXx",  # Star Atlas
    "POLIS": "poLisWXnNRwC6oBu1vHiuKQzFjGL4XDSu4g9qjz9qVk",  # Star Atlas DAO
    "MNGO": "MangoCzJ36AjZyKwVj3VnYU4GTonjfVEnJmvvWaxLac",  # Mango
    "COPE": "8HGyAAB1yoM1ttS7pXjHMa3dukTFGQggnFFH3hJZgzQh",  # Cope
    "FIDA": "EchesyfXePKdLtoiZSL8pBe8Myagyy8ZRqsACNCFGnvp",  # Bonfida
    "SAMO": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",  # Samoyed
    "SHDW": "SHDWyBxihqiCj6YekG2GUr7wqKLeLAMK1gHZck9pL6y",  # Shadow
    "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # Bonk
    "WIF": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",  # Dogwifhat
    "POPCAT": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",  # Popcat
}

class SwapMode(Enum):
    """Available swap modes"""
    EXACT_IN = "ExactIn"
    EXACT_OUT = "ExactOut"

@dataclass
class TokenInfo:
    """Token information structure"""
    address: str
    symbol: str
    name: str
    decimals: int
    logoURI: Optional[str] = None
    tags: List[str] = None
    daily_volume: Optional[float] = None
    freeze_authority: Optional[str] = None
    mint_authority: Optional[str] = None

@dataclass
class QuoteResponse:
    """Enhanced quote response"""
    input_mint: str
    in_amount: str
    output_mint: str
    out_amount: str
    other_amount_threshold: str
    swap_mode: str
    slippage_bps: int
    platform_fee: Optional[Dict] = None
    price_impact_pct: Optional[str] = None
    route_plan: Optional[List[Dict]] = None
    context_slot: Optional[int] = None
    time_taken: Optional[float] = None

@dataclass
class PriceData:
    """Price data structure"""
    token_address: str
    price: float
    price_change_24h: Optional[float] = None
    volume_24h: Optional[float] = None
    market_cap: Optional[float] = None
    timestamp: datetime = None

class JupiterAPIWrapper:
    """Enhanced Jupiter DEX API wrapper with proper token addresses"""

    def __init__(self):
        self.base_url = "https://quote-api.jup.ag/v6"
        self.price_api_url = "https://price.jup.ag/v4"
        self.session = None
        self.rate_limit_delay = 0.1  # 100ms between requests
        self.last_request_time = 0
        self.retry_attempts = 3
        self.timeout = 30

        # Caching
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes

        # Statistics
        self.request_count = 0
        self.error_count = 0
        self.cache_hits = 0

        # Token list cache
        self.tokens_cache = None
        self.tokens_cache_time = None

        logger.info("🪐 Jupiter API Wrapper initialized with proper token addresses")

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def get_token_mint_address(self, symbol: str) -> str:
        """Get the proper mint address for a token symbol"""
        if symbol in SOLANA_TOKEN_MINTS:
            return SOLANA_TOKEN_MINTS[symbol]
        else:
            # Try to find in cached tokens
            if self.tokens_cache:
                for token in self.tokens_cache:
                    if token.get("symbol") == symbol:
                        return token["address"]

            # Default to the symbol if not found (this might cause errors)
            logger.warning(f"⚠️ Token mint address not found for {symbol}, using symbol as fallback")
            return symbol

    def parse_trading_pair(self, pair: str) -> Tuple[str, str]:
        """Parse trading pair and return proper mint addresses"""
        if "/" in pair:
            base, quote = pair.split("/")
            base_mint = self.get_token_mint_address(base)
            quote_mint = self.get_token_mint_address(quote)
            return base_mint, quote_mint
        else:
            logger.warning(f"⚠️ Invalid trading pair format: {pair}")
            return pair, SOLANA_TOKEN_MINTS["USDC"]  # Default to USDC

    async def _make_request(self, method: str, url: str, **kwargs) -> Optional[Dict]:
        """Make HTTP request with rate limiting and retry logic"""
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)

        self.last_request_time = time.time()
        self.request_count += 1

        for attempt in range(self.retry_attempts):
            try:
                if not self.session:
                    self.session = aiohttp.ClientSession(
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    )

                async with self.session.request(method, url, **kwargs) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"HTTP {response.status} for {method} {url}: {error_text}")
                        if response.status == 429:  # Rate limited
                            await asyncio.sleep(2 ** attempt)
                            continue
                        else:
                            self.error_count += 1
                            return None

            except Exception as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == self.retry_attempts - 1:
                    self.error_count += 1
                    return None
                await asyncio.sleep(2 ** attempt)

        return None

    def _get_cache_key(self, *args) -> str:
        """Generate cache key from arguments"""
        return hashlib.md5(str(args).encode()).hexdigest()

    def _is_cache_valid(self, timestamp: datetime) -> bool:
        """Check if cache entry is still valid"""
        return (datetime.now() - timestamp).total_seconds() < self.cache_ttl

    async def get_quote(self, input_mint: str, output_mint: str, amount: int,
                       slippage_bps: int = 50, swap_mode: SwapMode = SwapMode.EXACT_IN) -> Optional[QuoteResponse]:
        """Get swap quote from Jupiter API"""
        cache_key = self._get_cache_key("quote", input_mint, output_mint, amount, slippage_bps)

        # Check cache first
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if self._is_cache_valid(timestamp):
                self.cache_hits += 1
                return cached_data

        # Ensure we have proper mint addresses
        if input_mint in SOLANA_TOKEN_MINTS:
            input_mint = SOLANA_TOKEN_MINTS[input_mint]
        if output_mint in SOLANA_TOKEN_MINTS:
            output_mint = SOLANA_TOKEN_MINTS[output_mint]

        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": amount,
            "slippageBps": slippage_bps,
            "swapMode": swap_mode.value,
        }

        url = f"{self.base_url}/quote"
        start_time = time.time()

        try:
            data = await self._make_request("GET", url, params=params)

            if data:
                quote_response = QuoteResponse(
                    input_mint=data["inputMint"],
                    in_amount=data["inAmount"],
                    output_mint=data["outputMint"],
                    out_amount=data["outAmount"],
                    other_amount_threshold=data["otherAmountThreshold"],
                    swap_mode=data["swapMode"],
                    slippage_bps=data["slippageBps"],
                    platform_fee=data.get("platformFee"),
                    price_impact_pct=data.get("priceImpactPct"),
                    route_plan=data.get("routePlan"),
                    context_slot=data.get("contextSlot"),
                    time_taken=time.time() - start_time
                )

                # Cache the result
                self.cache[cache_key] = (quote_response, datetime.now())

                return quote_response
            else:
                logger.error(f"Failed to get quote for {input_mint} -> {output_mint}")
                return None

        except Exception as e:
            logger.error(f"Error getting quote: {e}")
            logger.error(traceback.format_exc())
            return None

    async def get_swap_transaction(self, quote: Dict, user_public_key: str,
                                 wrap_and_unwrap_sol: bool = True,
                                 use_shared_accounts: bool = True,
                                 fee_account: Optional[str] = None) -> Optional[Dict]:
        """Get swap transaction from Jupiter API"""
        payload = {
            "quoteResponse": quote,
            "userPublicKey": user_public_key,
            "wrapAndUnwrapSol": wrap_and_unwrap_sol,
            "useSharedAccounts": use_shared_accounts,
        }

        if fee_account:
            payload["feeAccount"] = fee_account

        url = f"{self.base_url}/swap"
        return await self._make_request("POST", url, json=payload)

    async def get_tokens_list(self, force_refresh: bool = False) -> List[TokenInfo]:
        """Get list of available tokens"""
        if not force_refresh and self.tokens_cache and self.tokens_cache_time:
            if self._is_cache_valid(self.tokens_cache_time):
                return self.tokens_cache

        url = f"{self.base_url}/tokens"
        data = await self._make_request("GET", url)

        if data:
            tokens = []
            for token_data in data:
                token_info = TokenInfo(
                    address=token_data["address"],
                    symbol=token_data["symbol"],
                    name=token_data["name"],
                    decimals=token_data["decimals"],
                    logoURI=token_data.get("logoURI"),
                    tags=token_data.get("tags", []),
                    daily_volume=token_data.get("daily_volume"),
                    freeze_authority=token_data.get("freeze_authority"),
                    mint_authority=token_data.get("mint_authority")
                )
                tokens.append(token_info)

            self.tokens_cache = tokens
            self.tokens_cache_time = datetime.now()
            return tokens
        else:
            logger.error("Failed to get tokens list")
            return []

    async def get_price(self, token_address: str) -> Optional[PriceData]:
        """Get token price from Jupiter Price API"""
        # Convert symbol to mint address if needed
        if token_address in SOLANA_TOKEN_MINTS:
            token_address = SOLANA_TOKEN_MINTS[token_address]

        cache_key = self._get_cache_key("price", token_address)

        # Check cache first
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if self._is_cache_valid(timestamp):
                self.cache_hits += 1
                return cached_data

        url = f"{self.price_api_url}/price"
        params = {"ids": token_address}

        try:
            data = await self._make_request("GET", url, params=params)

            if data and "data" in data and token_address in data["data"]:
                price_info = data["data"][token_address]

                price_data = PriceData(
                    token_address=token_address,
                    price=float(price_info["price"]),
                    price_change_24h=price_info.get("priceChange24h"),
                    volume_24h=price_info.get("volume24h"),
                    market_cap=price_info.get("marketCap"),
                    timestamp=datetime.now()
                )

                # Cache the result
                self.cache[cache_key] = (price_data, datetime.now())

                return price_data
            else:
                logger.warning(f"No price data found for {token_address}")
                return None

        except Exception as e:
            logger.error(f"Error getting price for {token_address}: {e}")
            return None

    async def get_prices_batch(self, token_addresses: List[str]) -> Dict[str, PriceData]:
        """Get multiple token prices in a batch"""
        # Convert symbols to mint addresses
        converted_addresses = []
        for addr in token_addresses:
            if addr in SOLANA_TOKEN_MINTS:
                converted_addresses.append(SOLANA_TOKEN_MINTS[addr])
            else:
                converted_addresses.append(addr)

        url = f"{self.price_api_url}/price"
        params = {"ids": ",".join(converted_addresses)}

        try:
            data = await self._make_request("GET", url, params=params)

            if data and "data" in data:
                prices = {}
                for token_address, price_info in data["data"].items():
                    price_data = PriceData(
                        token_address=token_address,
                        price=float(price_info["price"]),
                        price_change_24h=price_info.get("priceChange24h"),
                        volume_24h=price_info.get("volume24h"),
                        market_cap=price_info.get("marketCap"),
                        timestamp=datetime.now()
                    )
                    prices[token_address] = price_data

                return prices
            else:
                logger.warning("No price data found for batch request")
                return {}

        except Exception as e:
            logger.error(f"Error getting batch prices: {e}")
            return {}

    async def get_route_map(self) -> Optional[Dict]:
        """Get route map showing available swap routes"""
        url = f"{self.base_url}/route-map"
        return await self._make_request("GET", url)

    async def execute_swap(self, quote_data: Dict, user_pubkey: str) -> Dict:
        """Execute a swap (demo/simulation only)"""
        try:
            # Get swap transaction
            swap_tx = await self.get_swap_transaction(quote_data, user_pubkey)

            if swap_tx:
                # In a real implementation, you would:
                # 1. Sign the transaction with the user's private key
                # 2. Send the transaction to the Solana network
                # 3. Wait for confirmation

                # For demo purposes, we'll return success
                return {
                    "success": True,
                    "signature": "demo_signature_" + str(int(time.time())),
                    "message": "Swap executed successfully (demo mode)",
                    "input_amount": quote_data.get("inAmount", "0"),
                    "output_amount": quote_data.get("outAmount", "0"),
                    "price_impact": quote_data.get("priceImpactPct", "0")
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to get swap transaction"
                }

        except Exception as e:
            logger.error(f"Error executing swap: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_statistics(self) -> Dict:
        """Get API usage statistics"""
        cache_hit_rate = (self.cache_hits / max(self.request_count, 1)) * 100
        error_rate = (self.error_count / max(self.request_count, 1)) * 100

        return {
            "total_requests": self.request_count,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": f"{cache_hit_rate:.1f}%",
            "errors": self.error_count,
            "error_rate": f"{error_rate:.1f}%",
            "cache_size": len(self.cache),
            "supported_tokens": len(SOLANA_TOKEN_MINTS)
        }

    async def health_check(self) -> bool:
        """Check if Jupiter API is healthy"""
        try:
            # Try to get a simple quote
            quote = await self.get_quote(
                input_mint="SOL",
                output_mint="USDC",
                amount=1000000  # 1 SOL
            )
            return quote is not None
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

# Test and example usage
async def main():
    """Test Jupiter API wrapper"""
    async with JupiterAPIWrapper() as jupiter:
        logger.info("🧪 Testing Jupiter API Wrapper")

        # Health check
        healthy = await jupiter.health_check()
        logger.info(f"🏥 Health check: {'✅ PASS' if healthy else '❌ FAIL'}")

        # Get quote
        quote = await jupiter.get_quote(
            input_mint="SOL",
            output_mint="USDC",
            amount=1000000  # 1 SOL
        )

        if quote:
            logger.info(f"💰 Quote: {quote.in_amount} SOL → {quote.out_amount} USDC")
            logger.info(f"📊 Price impact: {quote.price_impact_pct}%")

        # Get prices
        prices = await jupiter.get_prices_batch(["SOL", "USDC", "RAY"])
        for token, price_data in prices.items():
            logger.info(f"💎 {token}: ${price_data.price:.4f}")

        # Statistics
        stats = jupiter.get_statistics()
        logger.info(f"📈 Statistics: {stats}")

if __name__ == "__main__":
    asyncio.run(main())
