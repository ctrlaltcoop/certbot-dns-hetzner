"""Tests for certbot_dns_hetzner.dns_hetzner."""

import unittest

from unittest import mock

from certbot.compat import os
from certbot.errors import PluginError
from certbot.plugins import dns_test_common
from certbot.plugins.dns_test_common import DOMAIN
from certbot.tests import util as test_util

from certbot_dns_hetzner.fakes import FAKE_API_TOKEN, FAKE_RECORD



patch_display_util = test_util.patch_display_util


class AuthenticatorTest(
    test_util.TempDirTestCase, dns_test_common.BaseAuthenticatorTest
):
    """
    Test for Hetzner DNS Authenticator
    """

    def setUp(self):
        super().setUp()
        from certbot_dns_hetzner.dns_hetzner import Authenticator  # pylint: disable=import-outside-toplevel

        path = os.path.join(self.tempdir, "fake_credentials.ini")
        dns_test_common.write(
            {
                "hetzner_api_token": FAKE_API_TOKEN,
            },
            path,
        )

        super().setUp()
        self.config = mock.MagicMock(
            hetzner_credentials=path, hetzner_propagation_seconds=0
        )  # don't wait during tests

        self.auth = Authenticator(self.config, "hetzner")

        self.mock_client = mock.MagicMock()
        # _get_ispconfig_client | pylint: disable=protected-access
        self.auth._get_hetzner_client = mock.MagicMock(
            return_value=self.mock_client)

    @patch_display_util()
    def test_perform(self, unused_mock_get_utility):
        self.mock_client.add_txt_record.return_value = FAKE_RECORD
        self.auth.perform([self.achall])
        self.mock_client.add_txt_record.assert_called_with(
            DOMAIN, "_acme-challenge." + DOMAIN + ".", mock.ANY
        )

    def test_perform_but_raises_plugin_error(self):
        self.mock_client.add_txt_record.side_effect = mock.MagicMock(
            side_effect=PluginError()
        )
        self.assertRaises(PluginError, self.auth.perform, [self.achall])
        self.mock_client.add_txt_record.assert_called_with(
            DOMAIN, "_acme-challenge." + DOMAIN + ".", mock.ANY
        )

    @patch_display_util()
    def test_cleanup(self, unused_mock_get_utility):
        self.mock_client.add_txt_record.return_value = FAKE_RECORD
        # _attempt_cleanup | pylint: disable=protected-access
        self.auth.perform([self.achall])
        self.auth._attempt_cleanup = True
        self.auth.cleanup([self.achall])

        self.mock_client.del_txt_record.assert_called_with(
            DOMAIN, "_acme-challenge." + DOMAIN + ".", mock.ANY
        )

    @patch_display_util()
    def test_cleanup_but_raises_plugin_error(self, unused_mock_get_utility):
        self.mock_client.add_txt_record.return_value = FAKE_RECORD
        self.mock_client.del_txt_record.side_effect = mock.MagicMock(
            side_effect=PluginError()
        )
        # _attempt_cleanup | pylint: disable=protected-access
        self.auth.perform([self.achall])
        self.auth._attempt_cleanup = True

        self.assertRaises(PluginError, self.auth.cleanup, [self.achall])
        self.mock_client.del_txt_record.assert_called_with(
            DOMAIN, "_acme-challenge." + DOMAIN + ".", mock.ANY
        )


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
