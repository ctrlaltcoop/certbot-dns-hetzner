"""Tests for certbot_dns_hetzner.dns_hetzner."""
# pylint: disable=protected-access

import unittest

from certbot.errors import PluginError
from certbot_dns_hetzner.dns_hetzner import Authenticator


class AuthenticatorTest(unittest.TestCase):
    def test_get_zone(self):
        self.assertEqual(Authenticator._get_zone("example.com"), "example.com")
        self.assertEqual(Authenticator._get_zone("www.example.com"), "example.com")
        self.assertEqual(Authenticator._get_zone("deep.nested.sub.example.com"), "example.com")
        self.assertEqual(Authenticator._get_zone("www.example.co.uk"), "example.co.uk")

    def test_get_relative_name(self):
        self.assertEqual(
            Authenticator._get_relative_name("_acme-challenge.www.example.com", "example.com"),
            "_acme-challenge.www",
        )
        self.assertEqual(
            Authenticator._get_relative_name("_acme-challenge.example.com", "example.com"),
            "_acme-challenge",
        )
        self.assertEqual(
            Authenticator._get_relative_name("example.com", "example.com"),
            "@",
        )
        self.assertEqual(
            Authenticator._get_relative_name("_acme-challenge.example.com.example.com", "example.com"),
            "_acme-challenge.example.com",
        )

    def test_get_zone_valid_domain(self):
        self.assertEqual(Authenticator._get_zone("example.com"), "example.com")

    def test_get_zone_valid_subdomain(self):
        self.assertEqual(Authenticator._get_zone("sub.example.com"), "example.com")

    def test_get_zone_invalid_domain_raises(self):
        with self.assertRaises(PluginError):
            Authenticator._get_zone("invalid")

    def test_get_zone_empty_domain_raises(self):
        with self.assertRaises(PluginError):
            Authenticator._get_zone("")


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
