"""Utilities for working with proxies.

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
    """Manages a list of proxies.

    This class manages a list of proxies, allowing for randomization, re-use, etc.
    """

    def __init__(
        self,
        proxies: list[str],
        reuse: bool = False,
        random_order: bool = False,
    ) -> None:
        """Initialize the proxy manager.

        Args:
            proxies (list[str]): List of proxy addresses.
            reuse (bool, optional): Whether to reuse proxies. Defaults to False.
            random_order (bool, optional): Whether to use random order. Defaults to False.
        """
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
        """Add additional proxy addresses.

        Args:
            proxies (list[str]): List of proxy addresses.
        """
        if include_duplicates:
            # Include duplicates
            self._proxy_store.extend(proxies)
        else:
            # Exclude duplicates
            self._proxy_store.extend(list(set(proxies) - set(self._proxy_store)))
        self._reset()

    def set_proxies(self, proxies: list[str]) -> None:
        """Set the proxy addresses.

        Note: This will clear all existing proxies.

        Args:
            proxies (list[str]): List of proxy addresses.
        """
        # Clear existing proxies
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
        """Check if can cycle to the next proxy address.

        Returns:
            bool: True if can cycle, False otherwise.
        """
        # Already locked
        if self._index == -1:
            return False
        # Out of proxies
        if (self._index + 1 == len(self._proxies)) and not self._reuse:
            return False
        return True

    def cycle(self) -> None:
        """Attempt to cycle to the next proxy address."""
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
        """Current proxy address.

        Returns:
            str | None: Current proxy, or None if no proxies.
        """
        return self._proxies[self._index] if self._index > -1 else None


def https_to_http(address: str) -> str:
    """Convert a HTTPS proxy address to HTTP.

    Args:
        address (str): HTTPS proxy address.

    Returns:
        str: HTTP proxy address.
    """
    if address.startswith("https://"):
        return "http" + address.removeprefix("https")
    if address.startswith("http://"):
        return address
    raise ValueError(f"Invalid proxy address: {address}")


def prepare_http_proxy_for_requests(address: str) -> dict[str, str]:
    """Prepare a HTTP(S) proxy address for use with the 'requests' library.

    Args:
        address (str): HTTP(S) proxy address.

    Returns:
        dict[str, str]: Dictionary of HTTP and HTTPS proxy addresses.

    Raises:
        ValueError: If the address does not start with 'http(s)://'.
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
