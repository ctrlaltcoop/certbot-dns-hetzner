"""Tests for certbot_dns_ispconfig.dns_ispconfig."""

import unittest

import mock

from certbot.compat import os
from certbot.errors import PluginError
from certbot.plugins import dns_test_common
from certbot.plugins.dns_test_common import DOMAIN
from certbot.tests import util as test_util

from certbot_dns_hetzner.fakes import FAKE_API_TOKEN, FAKE_RECORD
from certbot_dns_hetzner.hetzner_client import _ZoneNotFoundException


class AuthenticatorTest(
        test_util.TempDirTestCase,
        dns_test_common.BaseAuthenticatorTest
):
    """
    Test for Hetzner DNS Authenticator
    """
    def setUp(self):
        super(AuthenticatorTest, self).setUp()
        from certbot_dns_hetzner.dns_hetzner import Authenticator  # pylint: disable=import-outside-toplevel

        path = os.path.join(self.tempdir, 'fake_credentials.ini')
        dns_test_common.write(
            {
                'hetzner_api_token': FAKE_API_TOKEN,
            },
            path,
        )

        super(AuthenticatorTest, self).setUp()
        self.config = mock.MagicMock(
            hetzner_credentials=path, hetzner_propagation_seconds=0
        )  # don't wait during tests

        self.auth = Authenticator(self.config, 'hetzner')

        self.mock_client = mock.MagicMock()
        # _get_ispconfig_client | pylint: disable=protected-access
        self.auth._get_hetzner_client = mock.MagicMock(return_value=self.mock_client)

    def test_perform(self):
        self.mock_client.add_record.return_value = FAKE_RECORD
        self.auth.perform([self.achall])
        self.mock_client.add_record.assert_called_with(
            DOMAIN, 'TXT', '_acme-challenge.' + DOMAIN + '.', mock.ANY, mock.ANY
        )

    def test_perform_but_raises_zone_not_found(self):
        self.mock_client.add_record.side_effect = mock.MagicMock(side_effect=_ZoneNotFoundException(DOMAIN))
        self.assertRaises(
            PluginError,
            self.auth.perform, [self.achall]
        )
        self.mock_client.add_record.assert_called_with(
            DOMAIN, 'TXT', '_acme-challenge.' + DOMAIN + '.', mock.ANY, mock.ANY
        )

    def test_cleanup(self):
        self.mock_client.add_record.return_value = FAKE_RECORD
        # _attempt_cleanup | pylint: disable=protected-access
        self.auth.perform([self.achall])
        self.auth._attempt_cleanup = True
        self.auth.cleanup([self.achall])

        self.mock_client.delete_record_by_name.assert_called_with(DOMAIN, '_acme-challenge.' + DOMAIN + '.')

    def test_cleanup_but_connection_aborts(self):
        self.mock_client.add_record.return_value = FAKE_RECORD
        # _attempt_cleanup | pylint: disable=protected-access
        self.auth.perform([self.achall])
        self.auth._attempt_cleanup = True
        self.auth.cleanup([self.achall])

        self.mock_client.delete_record_by_name.assert_called_with(DOMAIN, '_acme-challenge.' + DOMAIN + '.')


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
