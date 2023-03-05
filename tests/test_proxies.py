import unittest

from wvutils.proxies import (
    ProxyManager,
    https_to_http,
    prepare_http_proxy_for_requests,
)


class TestProxies(unittest.TestCase):
    def test_https_to_http(self):
        # Test using HTTPS
        self.assertEqual(
            https_to_http("https://localhost:8080"),
            "http://localhost:8080",
        )
        # Test using HTTP
        self.assertEqual(
            https_to_http("http://localhost:8080"),
            "http://localhost:8080",
        )
        # Test using invalid (non-http/https) address
        with self.assertRaises(ValueError):
            https_to_http("localhost:8080")

    def test_prepare_http_proxy_for_requests(self):
        # Test using HTTP
        address = "https://localhost:8080"
        self.assertEqual(
            prepare_http_proxy_for_requests(address),
            {
                "https_proxy": "https://localhost:8080",
                "http_proxy": "http://localhost:8080",
                "HTTPS_PROXY": "https://localhost:8080",
                "HTTP_PROXY": "http://localhost:8080",
            },
        )
        # Test using HTTPS
        address = "http://localhost:8080"
        self.assertEqual(
            prepare_http_proxy_for_requests(address),
            {
                "https_proxy": "http://localhost:8080",
                "http_proxy": "http://localhost:8080",
                "HTTPS_PROXY": "http://localhost:8080",
                "HTTP_PROXY": "http://localhost:8080",
            },
        )
        # Test using invalid (non-http/https) address
        with self.assertRaises(ValueError):
            prepare_http_proxy_for_requests("localhost:8080")

    def test_proxy_manager(self):
        proxies = ["https://proxy1.com", "https://proxy2.com", "https://proxy3.com"]
        proxy_manager = ProxyManager(proxies, reuse=True)
        # First cycle
        self.assertEqual(proxy_manager.proxy, proxies[0])
        self.assertTrue(proxy_manager.can_cycle)
        # Second cycle
        proxy_manager.cycle()
        self.assertEqual(proxy_manager.proxy, proxies[1])
        self.assertTrue(proxy_manager.can_cycle)
        # Third cycle
        proxy_manager.cycle()
        self.assertEqual(proxy_manager.proxy, proxies[2])
        self.assertTrue(proxy_manager.can_cycle)
        # Cycle back to first proxy
        proxy_manager.cycle()
        self.assertEqual(proxy_manager.proxy, proxies[0])
        self.assertTrue(proxy_manager.can_cycle)

    def test_proxy_manager_no_reuse(self):
        proxies = ["https://proxy1.com", "https://proxy2.com", "https://proxy3.com"]
        proxy_manager = ProxyManager(proxies, reuse=False)
        # First cycle
        self.assertEqual(proxy_manager.proxy, proxies[0])
        self.assertTrue(proxy_manager.can_cycle)
        # Second cycle
        proxy_manager.cycle()
        self.assertEqual(proxy_manager.proxy, proxies[1])
        self.assertTrue(proxy_manager.can_cycle)
        # Third cycle
        proxy_manager.cycle()
        self.assertEqual(proxy_manager.proxy, proxies[2])
        self.assertFalse(proxy_manager.can_cycle)
        # Fourth cycle (no proxies left)
        proxy_manager.cycle()
        self.assertIsNone(proxy_manager.proxy)
        self.assertFalse(proxy_manager.can_cycle)

    def test_proxy_manager_no_proxies(self):
        proxy_manager = ProxyManager([], reuse=True)
        # No proxies
        self.assertIsNone(proxy_manager.proxy)
        self.assertFalse(proxy_manager.can_cycle)
        # Still no proxies
        proxy_manager.cycle()

    def test_proxy_manager_no_proxies_no_reuse(self):
        proxy_manager = ProxyManager([], reuse=False)
        # No proxies
        self.assertIsNone(proxy_manager.proxy)
        self.assertFalse(proxy_manager.can_cycle)
        # Still no proxies
        proxy_manager.cycle()
        self.assertIsNone(proxy_manager.proxy)
        self.assertFalse(proxy_manager.can_cycle)
