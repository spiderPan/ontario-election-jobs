"""
Base scraper interface with built-in retry logic, jitter, and connection-reset resilience.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import asyncio
import random
import httpx
from models import MunicipalElectionPostings


class BaseScraper(ABC):
    def __init__(self, timeout: float = 20.0, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-CA,en-US;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Linux"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Connection": "close"  # Prevent stale keep-alive connection resets
        }

    async def safe_get(self, client: httpx.AsyncClient, url: str, headers: Optional[dict] = None) -> Optional[httpx.Response]:
        """Perform GET request with automatic retry on ConnectionReset or Network Errors."""
        req_headers = {**self.headers, **(headers or {})}
        
        for attempt in range(1, self.max_retries + 1):
            try:
                # Add small random jitter delay to prevent tripping rate limiters / WAFs
                await asyncio.sleep(random.uniform(0.2, 0.6))
                
                res = await client.get(
                    url,
                    headers=req_headers,
                    follow_redirects=True,
                    timeout=self.timeout
                )
                return res
            except (
                ConnectionResetError,
                httpx.RemoteProtocolError,
                httpx.ConnectError,
                httpx.ReadTimeout,
                httpx.ConnectTimeout,
                httpx.NetworkError,
                httpx.PoolTimeout
            ) as err:
                if attempt == self.max_retries:
                    # Silently return None on final retry failure rather than crashing
                    return None
                
                # Exponential backoff with jitter (e.g., 0.8s, 1.6s, 3.2s)
                backoff = (2 ** attempt) * 0.4 + random.uniform(0.1, 0.5)
                await asyncio.sleep(backoff)
            except Exception:
                return None

        return None

    @abstractmethod
    async def scrape(self, client: httpx.AsyncClient) -> List[MunicipalElectionPostings]:
        pass
