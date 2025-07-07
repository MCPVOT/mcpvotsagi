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
    """Enhanced Jupiter DEX API wrapper with advanced features"""

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

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _get_cache_key(self, endpoint: str, params: Dict = None) -> str:
        """Generate cache key for request"""
        key_data = f"{endpoint}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _is_cache_valid(self, cache_time: datetime) -> bool:
        """Check if cache is still valid"""
        return datetime.now() - cache_time < timedelta(seconds=self.cache_ttl)

    async def _make_request(self, endpoint: str, params: Dict = None,
                           method: str = "GET", data: Dict = None,
                           use_cache: bool = True) -> Optional[Dict]:
        """Make HTTP request with enhanced error handling, retry logic, and caching"""

        # Check cache first
        if use_cache and method == "GET":
            cache_key = self._get_cache_key(endpoint, params)
            if cache_key in self.cache:
                cached_data, cache_time = self.cache[cache_key]
                if self._is_cache_valid(cache_time):
                    self.cache_hits += 1
                    logger.debug(f"Cache hit for {endpoint}")
                    return cached_data

        # Rate limiting
        now = time.time()
        if now - self.last_request_time < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - (now - self.last_request_time))

        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )

        url = f"{self.base_url}/{endpoint}"

        # Retry logic
        for attempt in range(self.retry_attempts):
            try:
                self.request_count += 1

                if method == "GET":
                    async with self.session.get(url, params=params) as response:
                        return await self._handle_response(response, endpoint, params, use_cache)
                else:
                    async with self.session.post(url, json=data, params=params) as response:
                        return await self._handle_response(response, endpoint, params, use_cache)

            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1}/{self.retry_attempts} for {endpoint}")
                if attempt == self.retry_attempts - 1:
                    self.error_count += 1
                    logger.error(f"Request timed out after {self.retry_attempts} attempts")
                    return None
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

            except Exception as e:
                logger.error(f"Request error on attempt {attempt + 1}/{self.retry_attempts}: {e}")
                if attempt == self.retry_attempts - 1:
                    self.error_count += 1
                    logger.error(f"Request failed after {self.retry_attempts} attempts")
                    return None
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

        self.last_request_time = time.time()
        return None

    async def _handle_response(self, response: aiohttp.ClientResponse, endpoint: str,
                              params: Dict = None, use_cache: bool = True) -> Optional[Dict]:
        """Handle HTTP response with caching"""
        self.last_request_time = time.time()

        if response.status == 200:
            result = await response.json()

            # Cache the result
            if use_cache and params:
                cache_key = self._get_cache_key(endpoint, params)
                self.cache[cache_key] = (result, datetime.now())

                # Clean old cache entries
                if len(self.cache) > 1000:  # Limit cache size
                    await self._clean_cache()

            return result
        else:
            logger.error(f"HTTP {response.status} for {endpoint}: {await response.text()}")
            return None

    async def _clean_cache(self):
        """Clean expired cache entries"""
        current_time = datetime.now()
        expired_keys = []

        for key, (data, cache_time) in self.cache.items():
            if current_time - cache_time >= timedelta(seconds=self.cache_ttl):
                expired_keys.append(key)

        for key in expired_keys:
            del self.cache[key]

        logger.debug(f"Cleaned {len(expired_keys)} expired cache entries")

    async def get_quote(self, input_mint: str, output_mint: str, amount: int,
                       slippage_bps: int = 50, swap_mode: SwapMode = SwapMode.EXACT_IN,
                       platform_fee_bps: Optional[int] = None) -> Optional[QuoteResponse]:
        """Get enhanced quote for token swap"""
        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": amount,
            "slippageBps": slippage_bps,
            "swapMode": swap_mode.value
        }

        if platform_fee_bps is not None:
            params["platformFeeBps"] = platform_fee_bps

        result = await self._make_request("quote", params)
        if result:
            logger.info(f"Quote: {amount} {input_mint} -> {result.get('outAmount', 0)} {output_mint}")

            # Parse into structured response
            return QuoteResponse(
                input_mint=result.get("inputMint", input_mint),
                in_amount=result.get("inAmount", str(amount)),
                output_mint=result.get("outputMint", output_mint),
                out_amount=result.get("outAmount", "0"),
                other_amount_threshold=result.get("otherAmountThreshold", "0"),
                swap_mode=result.get("swapMode", swap_mode.value),
                slippage_bps=result.get("slippageBps", slippage_bps),
                platform_fee=result.get("platformFee"),
                price_impact_pct=result.get("priceImpactPct"),
                route_plan=result.get("routePlan"),
                context_slot=result.get("contextSlot"),
                time_taken=result.get("timeTaken")
            )

        return None

    async def get_swap_transaction(self, quote: Dict, user_public_key: str,
                                  wrap_and_unwrap_sol: bool = True,
                                  use_shared_accounts: bool = True,
                                  as_legacy_transaction: bool = False) -> Optional[Dict]:
        """Get enhanced swap transaction from quote"""
        if not quote:
            return None

        data = {
            "quoteResponse": quote,
            "userPublicKey": user_public_key,
            "wrapAndUnwrapSol": wrap_and_unwrap_sol,
            "useSharedAccounts": use_shared_accounts,
            "asLegacyTransaction": as_legacy_transaction
        }

        try:
            if not self.session:
                self.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                )

            async with self.session.post(f"{self.base_url}/swap", json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Swap transaction created for {user_public_key}")
                    return result
                else:
                    logger.error(f"Swap transaction failed: {response.status}")
                    return None

        except Exception as e:
            logger.error(f"Swap transaction error: {e}")
            return None

    async def get_tokens(self, strict_list: bool = False) -> Optional[List[TokenInfo]]:
        """Get all available tokens with enhanced parsing"""

        # Check cache first
        if self.tokens_cache and self.tokens_cache_time:
            if self._is_cache_valid(self.tokens_cache_time):
                logger.debug("Using cached token list")
                return self.tokens_cache

        endpoint = "tokens" if not strict_list else "tokens/strict"
        result = await self._make_request(endpoint, use_cache=False)

        if result and isinstance(result, list):
            tokens = []
            for token_data in result:
                try:
                    token = TokenInfo(
                        address=token_data.get("address", ""),
                        symbol=token_data.get("symbol", ""),
                        name=token_data.get("name", ""),
                        decimals=token_data.get("decimals", 0),
                        logoURI=token_data.get("logoURI"),
                        tags=token_data.get("tags", []),
                        daily_volume=token_data.get("daily_volume"),
                        freeze_authority=token_data.get("freeze_authority"),
                        mint_authority=token_data.get("mint_authority")
                    )
                    tokens.append(token)
                except Exception as e:
                    logger.warning(f"Error parsing token data: {e}")
                    continue

            # Cache the result
            self.tokens_cache = tokens
            self.tokens_cache_time = datetime.now()

            logger.info(f"Retrieved {len(tokens)} tokens")
            return tokens

        return None

    async def get_price(self, token_address: str) -> Optional[PriceData]:
        """Get current price for a token with enhanced data"""
        params = {"ids": token_address}

        # Use price API endpoint
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                )

            url = f"{self.price_api_url}/price"

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()

                    if "data" in result:
                        price_data = result["data"].get(token_address, {})
                        if price_data:
                            logger.info(f"Price for {token_address}: ${price_data.get('price', 0)}")

                            return PriceData(
                                token_address=token_address,
                                price=float(price_data.get("price", 0)),
                                price_change_24h=price_data.get("price_change_24h"),
                                volume_24h=price_data.get("volume_24h"),
                                market_cap=price_data.get("market_cap"),
                                timestamp=datetime.now()
                            )
                else:
                    logger.error(f"Price API error: {response.status}")

        except Exception as e:
            logger.error(f"Price request error: {e}")

        return None

    async def get_prices(self, token_addresses: List[str]) -> Optional[Dict[str, PriceData]]:
        """Get prices for multiple tokens"""
        params = {"ids": ",".join(token_addresses)}

        try:
            if not self.session:
                self.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                )

            url = f"{self.price_api_url}/price"

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()

                    if "data" in result:
                        prices = {}
                        for token_addr, price_data in result["data"].items():
                            prices[token_addr] = PriceData(
                                token_address=token_addr,
                                price=float(price_data.get("price", 0)),
                                price_change_24h=price_data.get("price_change_24h"),
                                volume_24h=price_data.get("volume_24h"),
                                market_cap=price_data.get("market_cap"),
                                timestamp=datetime.now()
                            )

                        logger.info(f"Retrieved prices for {len(prices)} tokens")
                        return prices
                else:
                    logger.error(f"Prices API error: {response.status}")

        except Exception as e:
            logger.error(f"Prices request error: {e}")

        return None

    async def get_route_map(self) -> Optional[Dict]:
        """Get route map for all available swaps"""
        result = await self._make_request("route-map")
        if result:
            logger.info("Retrieved route map")
        return result

    async def get_indexed_route_map(self) -> Optional[Dict]:
        """Get indexed route map for faster lookups"""
        result = await self._make_request("indexed-route-map")
        if result:
            logger.info("Retrieved indexed route map")
        return result

    def get_statistics(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "cache_hits": self.cache_hits,
            "cache_size": len(self.cache),
            "error_rate": self.error_count / max(self.request_count, 1),
            "cache_hit_rate": self.cache_hits / max(self.request_count, 1)
        }

    async def health_check(self) -> bool:
        """Check API health"""
        try:
            result = await self._make_request("health", use_cache=False)
            return result is not None
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def close(self):
        """Close the session and cleanup"""
        if self.session:
            await self.session.close()
            self.session = None

        # Clear cache
        self.cache.clear()
        self.tokens_cache = None
        self.tokens_cache_time = None

        logger.info("Jupiter API wrapper closed")

    # Legacy method for backward compatibility
    async def execute_swap(self, quote_data: Dict, user_pubkey: str) -> Dict:
        """Execute swap using Jupiter (legacy compatibility)"""
        return await self.get_swap_transaction(quote_data, user_pubkey)

# Test function
async def test_jupiter_api():
    """Test Jupiter API wrapper"""
    async with JupiterAPIWrapper() as jupiter:
        # Test health check
        health = await jupiter.health_check()
        print(f"Health check: {health}")

        # Test token list
        tokens = await jupiter.get_tokens()
        print(f"Retrieved {len(tokens) if tokens else 0} tokens")

        # Test quote
        if tokens and len(tokens) >= 2:
            quote = await jupiter.get_quote(
                input_mint=tokens[0].address,
                output_mint=tokens[1].address,
                amount=1000000
            )
            print(f"Quote: {quote}")

        # Test price
        if tokens:
            price = await jupiter.get_price(tokens[0].address)
            print(f"Price: {price}")

        # Show statistics
        stats = jupiter.get_statistics()
        print(f"Statistics: {stats}")

if __name__ == "__main__":
    asyncio.run(test_jupiter_api())