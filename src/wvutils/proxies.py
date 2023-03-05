"""Proxy Utilities

This module provides utilities for working with proxies.
"""

import logging
import random

__all__ = [
    "ProxyManager",
    "https_to_http",
    "prepare_http_proxy_for_requests",
]

logger = logging.getLogger(__name__)


class ProxyManager:
    """Proxy Manager

    This class manages a list of proxies and provides a simple interface for
    retrieving them. It also provides the ability to re-order the list of
    proxies, and to re-use proxies.
    """

    def __init__(
        self,
        proxies: list[str],
        reuse: bool = False,
        random_order: bool = False,
    ) -> None:
        # Unordered storage of proxy values
        self._proxy_store: list[str] = proxies.copy()
        self._reuse: bool = reuse
        self._random_order: bool = random_order

        # Active proxies (re-ordered etc.)
        self._proxies: list[str] = []
        # State (index -1 if no proxies, otherwise 0)
        self._index: int = -1
        # Initialize
        self._reset()

    def add_proxies(self, proxies: list[str], include_duplicates: bool = False) -> None:
        """Add New Proxy Addresses

        Args:
            proxies (list[str]): List of proxies to add.
        """
        if include_duplicates:
            # Include duplicates
            self._proxy_store.extend(proxies)
        else:
            # Exclude duplicates
            self._proxy_store.extend(list(set(proxies) - set(self._proxy_store)))
        self._reset()

    def set_proxies(self, proxies: list[str]) -> None:
        """Replace All Proxy Addresses

        Args:
            proxies (list[str]): List of proxies
        """
        self._proxy_store.clear()
        # Add new proxies
        self.add_proxies(proxies)

    def _reset(self) -> None:
        """Full Internal Reset"""
        # Refill and prepare working proxies from store
        self._proxies = self._proxy_store.copy()
        if self._random_order:
            random.shuffle(self._proxies)
        # Starting index
        self._index = -1 if len(self._proxies) == 0 else 0

    @property
    def can_cycle(self) -> bool:
        """Whether the Proxy Manager Can Cycle to the Next Proxy

        Returns:
            bool: True if can cycle to next proxy, False otherwise.
        """
        # Already locked
        if self._index == -1:
            return False
        # Out of proxies
        if (self._index + 1 == len(self._proxies)) and not self._reuse:
            return False
        return True

    def cycle(self) -> None:
        """User Method to Attempt to Increment the Index of the Current Proxy"""
        # Cannot cycle when locked
        if self._index > -1:
            # Increment to next
            self._index += 1
            if self._index + 1 > len(self._proxies):
                # Passed end of list
                if self._reuse:
                    # Full reset
                    self._reset()
                else:
                    # Lock - Out of proxies
                    self._index = -1
        else:
            # TODO: Should raise or use 'warnings' module?
            logger.warning("Attempted to cycle proxies after having ran out previously")

    @property
    def proxy(self) -> str | None:
        """Current Proxy

        Returns:
            str | None: Current proxy or None if no proxies.
        """
        return self._proxies[self._index] if self._index > -1 else None


def https_to_http(address: str) -> str:
    """Convert an HTTPS Proxy Address to HTTP

    Args:
        address (str): HTTPS proxy address

    Returns:
        str: HTTP proxy address
    """
    if address.startswith("https://"):
        return "http" + address.removeprefix("https")
    if address.startswith("http://"):
        return address
    raise ValueError(f"Invalid proxy address: {address}")


def prepare_http_proxy_for_requests(address: str) -> dict[str, str]:
    """Prepare a HTTP(S) Proxy Address for use with Requests

    Args:
        address (str): HTTP(S) Proxy address

    Returns:
        dict[str, str]: Dictionary of proxy addresses

    Raises:
        ValueError: If the address is not a valid HTTP(S) proxy address.
    """
    if address.startswith("https://"):
        return {
            "HTTPS_PROXY": address,
            "HTTP_PROXY": https_to_http(address),
            "https_proxy": address,
            "http_proxy": https_to_http(address),
        }
    elif address.startswith("http://"):
        return {
            "HTTPS_PROXY": address,
            "HTTP_PROXY": address,
            "https_proxy": address,
            "http_proxy": address,
        }
    raise ValueError(f"Invalid proxy address: {address}")
