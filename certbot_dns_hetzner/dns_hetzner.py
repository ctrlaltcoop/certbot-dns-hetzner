"""DNS Authenticator for Hetzner DNS."""
import requests

import zope.interface

from certbot import errors
from certbot import interfaces
from certbot.plugins import dns_common

from certbot_dns_hetzner.hetzner_client import \
    _MalformedResponseException, \
    _HetznerClient, \
    _ZoneNotFoundException, _NotAuthorizedException

TTL = 60


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Hetzner
    This Authenticator uses the Hetzner DNS API to fulfill a dns-01 challenge.
    """

    description = 'Obtain certificates using a DNS TXT record (if you are using Hetzner for DNS).'

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds=60)
        add('credentials', help='Hetzner credentials INI file.')

    def more_info(self):  # pylint: disable=missing-function-docstring,no-self-use
        return 'This plugin configures a DNS TXT record to respond to a dns-01 challenge using ' + \
               'the Hetzner API.'

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            'credentials',
            'Hetzner credentials INI file',
            {
                'api_token': 'Hetzner API Token from \'https://dns.hetzner.com/settings/api-token\'',
            }
        )

    def _perform(self, domain, validation_name, validation):
        try:
            self._get_hetzner_client().add_record(
                domain,
                "TXT",
                self._fqdn_format(validation_name),
                validation,
                TTL
            )
        except (
                _ZoneNotFoundException,
                requests.ConnectionError,
                _MalformedResponseException,
                _NotAuthorizedException
        ) as exception:
            raise errors.PluginError(exception)

    def _cleanup(self, domain, validation_name, validation):
        try:
            self._get_hetzner_client().delete_record_by_name(domain, self._fqdn_format(validation_name))
        except (requests.ConnectionError, _NotAuthorizedException) as exception:
            raise errors.PluginError(exception)

    def _get_hetzner_client(self):
        return _HetznerClient(
            self.credentials.conf('api_token'),
        )

    @staticmethod
    def _fqdn_format(name):
        if not name.endswith('.'):
            return '{0}.'.format(name)
        return name
