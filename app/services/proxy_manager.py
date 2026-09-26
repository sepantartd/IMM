"""
Proxy & Session manager service module for IMM.
Handles proxy verification, round-robin proxy rotation, and HTTP client integration.
"""

import httpx
from typing import List, Optional, Dict, Any
from itertools import cycle
from app.utils.logger import logger


class ProxyManagerService:
    """Service for validating, storing, and rotating proxies for network requests."""

    def __init__(self, proxy_list: Optional[List[str]] = None):
        self._proxies: List[str] = proxy_list if proxy_list else []
        self._active_proxies: List[str] = []
        self._proxy_cycle = None
        if self._proxies:
            self.refresh_active_proxies()

    def set_proxies(self, proxy_list: List[str]) -> None:
        """Sets new list of proxy strings (e.g., 'http://user:pass@host:port')."""
        self._proxies = [p.strip() for p in proxy_list if p.strip()]
        self.refresh_active_proxies()

    def verify_proxy(self, proxy_url: str, timeout: float = 5.0) -> bool:
        """Verifies if a proxy is functional by making a test request."""
        try:
            with httpx.Client(proxies=proxy_url, timeout=timeout) as client:
                res = client.get("https://www.instagram.com/robots.txt")
                return res.status_code == 200
        except Exception as e:
            logger.debug(f"Proxy check failed for '{proxy_url}': {e}")
            return False

    def refresh_active_proxies(self) -> int:
        """Filters out non-working proxies and updates the active rotation pool."""
        logger.info(f"Verifying {len(self._proxies)} proxies...")
        valid_proxies = []

        for proxy in self._proxies:
            if self.verify_proxy(proxy):
                valid_proxies.append(proxy)
                logger.info(f"Proxy active and verified: {proxy}")
            else:
                logger.warning(f"Proxy unreachable or dead: {proxy}")

        self._active_proxies = valid_proxies
        if self._active_proxies:
            self._proxy_cycle = cycle(self._active_proxies)
        else:
            self._proxy_cycle = None

        logger.info(f"Proxy refresh complete: {len(self._active_proxies)} active proxies available.")
        return len(self._active_proxies)

    def get_next_proxy(self) -> Optional[str]:
        """Returns the next healthy proxy from the rotation cycle."""
        if not self._proxy_cycle or not self._active_proxies:
            return None
        return next(self._proxy_cycle)

    def get_status(self) -> Dict[str, Any]:
        """Returns summary of proxy pool status."""
        return {
            "total_configured": len(self._proxies),
            "active_proxies": len(self._active_proxies),
            "has_rotation": self._proxy_cycle is not None
                                 }
      
